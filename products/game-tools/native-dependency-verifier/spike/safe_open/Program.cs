using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using Microsoft.Win32.SafeHandles;

// Experimental handle-relative admission test. Not production security code.
if (!OperatingSystem.IsWindows() || args.Length is < 2 or > 3 ||
    (args.Length == 3 && args[2] is not ("--hold" or "--pe")))
{
    Console.Error.WriteLine("usage: SafeOpenProbe <local-root-directory> <relative-file> [--hold|--pe]");
    return 2;
}

var held = new List<SafeFileHandle>();
try
{
    string root = Path.GetFullPath(args[0]);
    if (root.Length < 3 || !char.IsAsciiLetter(root[0]) || root[1] != ':' || root[2] != '\\')
        throw new InvalidDataException("Only drive-letter local paths are in this experiment");
    string relative = args[1];
    string[] pieces = relative.Split('\\');
    if (pieces.Length is < 1 or > 32 || pieces.Any(p => p is "" or "." or ".." ||
        p.IndexOfAny(new[] { '/', ':', '\0' }) >= 0 || p.EndsWith(' ') || p.EndsWith('.')))
        throw new InvalidDataException("Unsupported relative path");

    var rootHandle = Native.Open(Native.ToDevicePath(root), IntPtr.Zero, true);
    held.Add(rootHandle);
    Native.Validate(rootHandle, directory: true);
    SafeFileHandle parent = rootHandle;
    for (int i = 0; i < pieces.Length; i++)
    {
        bool directory = i < pieces.Length - 1;
        var handle = Native.Open(pieces[i], parent.DangerousGetHandle(), directory);
        held.Add(handle);
        Native.Validate(handle, directory);
        parent = handle;
    }
    using var stream = new FileStream(parent, FileAccess.Read);
    if (stream.Length > 64L * 1024 * 1024) throw new InvalidDataException("File too large");
    string digest = Convert.ToHexString(SHA256.HashData(stream));
    if (args.Length == 3 && args[2] == "--pe")
    {
        stream.Position = 0;
        var pe = PeParser.Inspect(stream);
        Console.WriteLine(System.Text.Json.JsonSerializer.Serialize(new { sha256 = digest, pe }));
    }
    else Console.WriteLine($"OPENED {digest}");
    if (args.Length == 3 && args[2] == "--hold")
    {
        Console.Out.Flush();
        Console.ReadLine();
        stream.Position = 0;
        Console.WriteLine($"AFTER {Convert.ToHexString(SHA256.HashData(stream))}");
    }
    return 0;
}
catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidDataException or
                           Win32Exception or ArgumentException or NotSupportedException or BadImageFormatException or OverflowException)
{
    Console.Error.WriteLine($"INCOMPLETE {ex.Message}");
    return 2;
}
finally
{
    foreach (var handle in held) handle.Dispose();
}

internal static class Native
{
    const uint ObjCaseInsensitive = 0x40;
    const uint ObjDontReparse = 0x1000;
    const uint Synchronize = 0x00100000;
    const uint ReadAttributes = 0x80;
    const uint ReadDataOrListDirectory = 0x1;
    const uint ShareRead = 0x1;
    const uint FileOpen = 0x1;
    const uint DirectoryFile = 0x1;
    const uint NonDirectoryFile = 0x40;
    const uint SynchronousNonAlert = 0x20;
    const uint OpenReparsePoint = 0x00200000;
    const uint ReparseAttribute = 0x400;
    const uint DirectoryAttribute = 0x10;

    [StructLayout(LayoutKind.Sequential)]
    struct UnicodeString { public ushort Length, MaximumLength; public IntPtr Buffer; }
    [StructLayout(LayoutKind.Sequential)]
    struct ObjectAttributes
    {
        public int Length; public IntPtr RootDirectory, ObjectName; public uint Attributes;
        public IntPtr SecurityDescriptor, SecurityQualityOfService;
    }
    [StructLayout(LayoutKind.Sequential)]
    struct IoStatusBlock { public IntPtr Status; public UIntPtr Information; }
    [StructLayout(LayoutKind.Sequential)]
    struct FileInformation
    {
        public uint Attributes, CreationLow, CreationHigh, AccessLow, AccessHigh, WriteLow, WriteHigh,
                    VolumeSerial, SizeHigh, SizeLow, NumberOfLinks, IndexHigh, IndexLow;
    }

    [DllImport("ntdll.dll")]
    static extern int NtCreateFile(out SafeFileHandle handle, uint access, ref ObjectAttributes attributes,
        out IoStatusBlock status, IntPtr allocationSize, uint fileAttributes, uint shareAccess,
        uint disposition, uint options, IntPtr eaBuffer, uint eaLength);
    [DllImport("ntdll.dll")]
    static extern uint RtlNtStatusToDosError(int status);
    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool GetFileInformationByHandle(SafeFileHandle handle, out FileInformation information);
    [DllImport("kernel32.dll", SetLastError = true)]
    static extern uint GetFileType(SafeFileHandle handle);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    static extern uint QueryDosDeviceW(string deviceName, System.Text.StringBuilder targetPath, int max);

    public static string ToDevicePath(string root)
    {
        var target = new System.Text.StringBuilder(32768);
        if (QueryDosDeviceW(root[..2], target, target.Capacity) == 0)
            throw new Win32Exception(Marshal.GetLastWin32Error(), "Cannot resolve drive device");
        string device = target.ToString();
        if (!device.StartsWith("\\Device\\HarddiskVolume", StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException("Unsupported drive device");
        return device + root[2..];
    }

    public static SafeFileHandle Open(string name, IntPtr root, bool directory)
    {
        if (name.Length > 32766) throw new InvalidDataException("Path too long");
        IntPtr buffer = Marshal.StringToHGlobalUni(name);
        IntPtr unicodePtr = IntPtr.Zero;
        try
        {
            var unicode = new UnicodeString { Length = checked((ushort)(name.Length * 2)),
                MaximumLength = checked((ushort)((name.Length + 1) * 2)), Buffer = buffer };
            unicodePtr = Marshal.AllocHGlobal(Marshal.SizeOf<UnicodeString>());
            Marshal.StructureToPtr(unicode, unicodePtr, false);
            var attributes = new ObjectAttributes { Length = Marshal.SizeOf<ObjectAttributes>(),
                RootDirectory = root, ObjectName = unicodePtr, Attributes = ObjCaseInsensitive | ObjDontReparse };
            uint options = SynchronousNonAlert | (directory ? DirectoryFile : NonDirectoryFile | OpenReparsePoint);
            int status = NtCreateFile(out var handle, Synchronize | ReadAttributes | ReadDataOrListDirectory,
                ref attributes, out _, IntPtr.Zero, 0, ShareRead, FileOpen, options, IntPtr.Zero, 0);
            // This experiment accepts only synchronous STATUS_SUCCESS; a pending
            // or informational status is incomplete rather than assumed open.
            if (status != 0)
            {
                handle?.Dispose();
                throw new Win32Exception((int)RtlNtStatusToDosError(status), $"NT status 0x{status:X8}");
            }
            return handle;
        }
        finally
        {
            if (unicodePtr != IntPtr.Zero) Marshal.FreeHGlobal(unicodePtr);
            Marshal.FreeHGlobal(buffer);
        }
    }

    public static void Validate(SafeFileHandle handle, bool directory)
    {
        if (GetFileType(handle) != 1 || !GetFileInformationByHandle(handle, out var info))
            throw new Win32Exception(Marshal.GetLastWin32Error(), "Cannot inspect opened file handle");
        if ((info.Attributes & ReparseAttribute) != 0 || ((info.Attributes & DirectoryAttribute) != 0) != directory)
            throw new InvalidDataException("Reparse point or unexpected object type");
        if (!directory && info.NumberOfLinks != 1)
            throw new InvalidDataException("Hardlinked file is unsupported");
    }
}
