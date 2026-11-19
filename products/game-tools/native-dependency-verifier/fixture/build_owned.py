"""Build the owned Godot/PE experiment into a new, disposable directory.

Requires Windows, MSVC developer setup scripts for x64 and x86, a Godot editor,
matching release template, and the Godot 4.4 C interface header. No downloads.
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

FIXTURE = Path(__file__).resolve().parent
UNSAFE_CMD_CHARS = set('"&|<>^%!\r\n')
CYCLE_OMIT = ('root.dll', 'middle.dll', 'fixture.exe', 'fixture.console.exe', 'fixture.pck')


def checked_cmd_path(path):
    value = str(path)
    if any(ch in value for ch in UNSAFE_CMD_CHARS):
        raise ValueError('MSVC command path contains unsupported cmd.exe characters')
    return value


def compile_dll(vcvars, build, source, output, extra=(), include=None, link=()):
    args = ['cl', '/nologo', '/LD']
    if include:
        args.append('/I' + checked_cmd_path(include))
    args += [checked_cmd_path(source), *[checked_cmd_path(item) for item in extra],
             '/link', *link, '/out:' + output]
    batch = build / 'compile-owned.cmd'
    batch.write_text('@echo off\r\ncall "' + checked_cmd_path(vcvars) + '" >nul\r\n'
                     'if errorlevel 1 exit /b 1\r\n' + subprocess.list2cmdline(args) + '\r\n', encoding='ascii')
    subprocess.run(['cmd.exe', '/d', '/c', checked_cmd_path(batch)], cwd=build, check=True, timeout=120)


def make_import_library(vcvars, build, definition, output):
    args = ['lib', '/nologo', '/machine:x64', '/def:' + checked_cmd_path(definition), '/out:' + output]
    batch = build / 'import-library-owned.cmd'
    batch.write_text('@echo off\r\ncall "' + checked_cmd_path(vcvars) + '" >nul\r\n'
                     'if errorlevel 1 exit /b 1\r\n' + subprocess.list2cmdline(args) + '\r\n', encoding='ascii')
    subprocess.run(['cmd.exe', '/d', '/c', checked_cmd_path(batch)], cwd=build, check=True, timeout=120)


def build_arch(vcvars, header, output, x86=False):
    output.mkdir()
    compile_dll(vcvars, output, FIXTURE / 'leaf.c', 'leaf.dll')
    compile_dll(vcvars, output, FIXTURE / 'middle.c', 'middle.dll', [output / 'leaf.lib'])
    compile_dll(vcvars, output, FIXTURE / 'root.c', 'root.dll', [output / 'middle.lib'])
    compile_dll(vcvars, output, FIXTURE / 'godot/extension.c', 'extension.dll',
                [output / 'root.lib'], include=header.parent)
    if x86:
        compile_dll(vcvars, output, FIXTURE / 'dynamic.c', 'dynamic.dll')


def create_project(output, build, template):
    shutil.copytree(FIXTURE / 'godot', output)
    bin_dir = output / 'addons/fixture/bin'
    bin_dir.mkdir()
    for name in ('extension.dll', 'root.dll', 'middle.dll', 'leaf.dll'):
        shutil.copyfile(build / name, bin_dir / name)
    template_path = template.as_posix()
    if '"' in template_path or '\n' in template_path:
        raise ValueError('unsupported template path')
    (output / 'export_presets.cfg').write_text('\n'.join([
        '[preset.0]', 'name="Windows Desktop"', 'platform="Windows Desktop"', 'runnable=true',
        'export_filter="all_resources"', 'include_filter=""', 'exclude_filter=""',
        'export_path=""', 'patch_list=PackedStringArray()', '', '[preset.0.options]',
        f'custom_template/release="{template_path}"', 'binary_format/architecture="x86_64"',
        'binary_format/embed_pck=false', '']), encoding='utf-8')


def run_godot(godot, project, args, log, env):
    result = subprocess.run([str(godot), '--headless', '--path', str(project), *args],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, timeout=180)
    log.write_bytes(result.stdout)
    return result.returncode


def export_project(godot, project, output, env):
    output.mkdir()
    status = run_godot(godot, project, ['--export-release', 'Windows Desktop', str(output / 'fixture.exe')],
                       output.parent / (output.name + '.log'), env)
    if status:
        raise RuntimeError(f'Godot export failed ({status}): {output.name}')


def copy_package(source, target, omit=()):
    target.mkdir()
    for file in source.iterdir():
        if file.is_file() and file.name not in omit:
            shutil.copyfile(file, target / file.name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('godot', 'template', 'header', 'vcvars64', 'vcvars32', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--debug-template', type=Path, help='optional matching Windows x64 debug template')
    args = parser.parse_args()
    for name in ('godot', 'template', 'header', 'vcvars64', 'vcvars32'):
        path = getattr(args, name).resolve(strict=True)
        if not path.is_file():
            raise ValueError(name + ' must name a file')
        setattr(args, name, path)
    if args.debug_template:
        args.debug_template = args.debug_template.resolve(strict=True)
        if not args.debug_template.is_file():
            raise ValueError('debug-template must name a file')
    if args.header.name.lower() != 'gdextension_interface.h':
        raise ValueError('header must be named gdextension_interface.h')
    version = subprocess.run([str(args.godot), '--version'], capture_output=True, text=True,
                             check=True, timeout=30).stdout.strip()
    if not version.startswith('4.7.2.stable.'):
        raise ValueError('this experiment expects Godot 4.7.2 stable; found ' + version)
    output = args.output.absolute()
    output.mkdir(parents=True, exist_ok=False)
    print('Building owned fixtures in', output, flush=True)
    build_arch(args.vcvars64, args.header, output / 'build-x64')
    build_arch(args.vcvars32, args.header, output / 'build-x86', x86=True)
    delay = output / 'delay-build'
    delay.mkdir()
    compile_dll(args.vcvars64, delay, FIXTURE / 'middle.c', 'middle-delay.dll',
                [output / 'build-x64/leaf.lib'], link=['delayimp.lib', '/delayload:leaf.dll'])
    wrong_dependency = output / 'wrong-dependency-build'
    wrong_dependency.mkdir()
    compile_dll(args.vcvars64, wrong_dependency, FIXTURE / 'fixture.c', 'root.dll')
    cycle = output / 'cycle-build'
    cycle.mkdir()
    make_import_library(args.vcvars64, cycle, FIXTURE / 'cycle_root.def', 'root_stub.lib')
    make_import_library(args.vcvars64, cycle, FIXTURE / 'cycle_middle.def', 'middle_stub.lib')
    compile_dll(args.vcvars64, cycle, FIXTURE / 'root.c', 'root.dll', [cycle / 'middle_stub.lib'])
    compile_dll(args.vcvars64, cycle, FIXTURE / 'cycle_middle.c', 'middle.dll', [cycle / 'root_stub.lib'])

    env = os.environ.copy()
    for key in ('APPDATA', 'LOCALAPPDATA'):
        path = output / key.lower()
        path.mkdir()
        env[key] = str(path)
    clean = output / 'clean-project'
    create_project(clean, output / 'build-x64', args.template)
    status = run_godot(args.godot, clean, ['--editor', '--import'], output / 'import.log', env)
    if status:
        raise RuntimeError(f'Godot import failed ({status})')
    export_project(args.godot, clean, output / 'export', env)
    for name, omitted in [('missing-direct', ('root.dll',)), ('missing-transitive', ('leaf.dll',)),
                          ('missing-extension', ('extension.dll',)),
                          ('wrong-arch-valid-symbol', ('extension.dll',)),
                          ('benign-transform', ('extension.dll',)),
                          ('misplaced-leaf', ('leaf.dll',)), ('replaced-dependency', ('root.dll',)),
                          ('delay-missing-export', ('middle.dll', 'leaf.dll')),
                          ('cycle-export', CYCLE_OMIT)]:
        copy_package(output / 'export', output / name, omitted)
    shutil.copyfile(output / 'build-x86/extension.dll', output / 'wrong-arch-valid-symbol/extension.dll')
    shutil.copyfile(output / 'export/extension.dll', output / 'benign-transform/extension.dll')
    with (output / 'benign-transform/extension.dll').open('ab') as stream:
        stream.write(b'GDM003-owned-test-overlay')
    shutil.copyfile(wrong_dependency / 'root.dll', output / 'replaced-dependency/root.dll')
    (output / 'misplaced-leaf/other').mkdir()
    shutil.copyfile(output / 'export/leaf.dll', output / 'misplaced-leaf/other/leaf.dll')
    shutil.copyfile(delay / 'middle-delay.dll', output / 'delay-missing-export/middle.dll')
    shutil.copyfile(cycle / 'root.dll', output / 'cycle-export/root.dll')
    shutil.copyfile(cycle / 'middle.dll', output / 'cycle-export/middle.dll')

    # Build independent project copies; editing their descriptors does not mutate
    # the clean project or rely on its imported editor cache.
    for name in ('omitted', 'nested', 'tag-fresh', 'tag-specific-missing', 'dependency-order', 'collision',
                 'dependency-collision', 'embedded', 'custom-feature', 'relative', 'multiline'):
        project = output / (name if name == 'tag-specific-missing' else name + '-project')
        create_project(project, output / 'build-x64', args.template)
        descriptor = project / 'addons/fixture/fixture.gdextension'
        text = descriptor.read_text(encoding='utf-8')
        if name in ('relative', 'multiline'):
            text = text.replace('res://addons/fixture/bin/', './bin/')
            if name == 'multiline':
                original = '{"./bin/root.dll": "", "./bin/middle.dll": "", "./bin/leaf.dll": ""}'
                if text.count(original) != 1:
                    raise ValueError('expected fixture dependency map exactly once')
                text = text.replace(original, '{\n    "./bin/root.dll": "",\n    "./bin/middle.dll": "",\n    "./bin/leaf.dll": "",\n}')
        elif name == 'custom-feature':
            bin_dir = project / 'addons/fixture/bin'
            shutil.copyfile(bin_dir / 'extension.dll', bin_dir / 'premium.dll')
            text = text.replace('windows.release.x86_64 =',
                                'windows.release.x86_64.premium = "res://addons/fixture/bin/premium.dll"\n'
                                'windows.release.x86_64 =')
            preset = project / 'export_presets.cfg'
            preset.write_text(preset.read_text(encoding='utf-8').replace('runnable=true',
                                                                        'runnable=true\ncustom_features="premium"'),
                              encoding='utf-8')
        elif name == 'embedded':
            preset = project / 'export_presets.cfg'
            preset.write_text(preset.read_text(encoding='utf-8').replace('binary_format/embed_pck=false',
                                                                        'binary_format/embed_pck=true'),
                              encoding='utf-8')
        elif name == 'omitted':
            text = text.replace(', "res://addons/fixture/bin/leaf.dll": ""', '')
        elif name == 'nested':
            text = text.replace('"res://addons/fixture/bin/leaf.dll": ""',
                                '"res://addons/fixture/bin/leaf.dll": "nested"')
        elif name == 'tag-fresh':
            text = text.replace('windows.release.x86_64 =',
                                'windows.release = "res://addons/fixture/bin/not-there.dll"\nwindows.release.x86_64 =')
        elif name == 'tag-specific-missing':
            text = text.replace('windows.release.x86_64 = "res://addons/fixture/bin/extension.dll"',
                                'windows.release = "res://addons/fixture/bin/extension.dll"\n'
                                'windows.release.x86_64 = "res://addons/fixture/bin/not-there.dll"')
        elif name == 'dependency-order':
            text = text.replace('[dependencies]', '[dependencies]\nwindows = '
                                '{"res://addons/fixture/bin/root.dll": "", '
                                '"res://addons/fixture/bin/middle.dll": ""}')
        elif name == 'collision':
            other = project / 'addons/other/bin'
            other.mkdir(parents=True)
            shutil.copyfile(output / 'build-x64/extension.dll', other / 'extension.dll')
            with (other / 'extension.dll').open('ab') as stream:
                stream.write(b'GDM003-owned-test-overlay')
            (other.parent / 'other.gdextension').write_text(
                '[configuration]\nentry_symbol = "fixture_init"\ncompatibility_minimum = "4.4"\n'
                '[libraries]\nwindows.debug.x86_64 = "res://addons/other/bin/extension.dll"\n'
                'windows.release.x86_64 = "res://addons/other/bin/extension.dll"\n', encoding='utf-8')
        elif name == 'dependency-collision':
            other = project / 'addons/other/bin'
            other.mkdir(parents=True)
            shutil.copyfile(output / 'build-x64/extension.dll', other / 'other_extension.dll')
            shutil.copyfile(wrong_dependency / 'root.dll', other / 'root.dll')
            (other.parent / 'other.gdextension').write_text(
                '[configuration]\nentry_symbol = "fixture_init"\ncompatibility_minimum = "4.4"\n'
                '[libraries]\nwindows.debug.x86_64 = "res://addons/other/bin/other_extension.dll"\n'
                'windows.release.x86_64 = "res://addons/other/bin/other_extension.dll"\n'
                '[dependencies]\nwindows.x86_64 = {"res://addons/other/bin/root.dll": ""}\n', encoding='utf-8')
        descriptor.write_text(text, encoding='utf-8')
        status = run_godot(args.godot, project, ['--editor', '--import'], output / (name + '-import.log'), env)
        if status:
            raise RuntimeError(f'Godot {name} import failed ({status})')
        target = output / ('dependency-order-export-retry' if name == 'dependency-order' else name + '-export')
        if name == 'tag-specific-missing':
            target.mkdir()
            status = run_godot(args.godot, project, ['--export-release', 'Windows Desktop', str(target / 'fixture.exe')],
                               output / (name + '-export.log'), env)
            if status == 0:
                raise RuntimeError('expected missing-specific-library export to fail')
        else:
            export_project(args.godot, project, target, env)
            if name == 'custom-feature':
                copy_package(target, output / 'custom-feature-missing', ('premium.dll',))
            if name == 'relative':
                copy_package(target, output / 'relative-missing-leaf', ('leaf.dll',))
            if name == 'multiline':
                copy_package(target, output / 'multiline-missing-leaf', ('leaf.dll',))
    if args.debug_template:
        project = output / 'debug-project'
        create_project(project, output / 'build-x64', args.template)
        preset = project / 'export_presets.cfg'
        debug_path = args.debug_template.as_posix()
        if '"' in debug_path or '\n' in debug_path:
            raise ValueError('unsupported debug-template path')
        preset.write_text(preset.read_text(encoding='utf-8').replace(
            '[preset.0.options]', '[preset.0.options]\ncustom_template/debug="' + debug_path + '"'),
            encoding='utf-8')
        status = run_godot(args.godot, project, ['--editor', '--import'], output / 'debug-import.log', env)
        if status:
            raise RuntimeError(f'Godot debug import failed ({status})')
        target = output / 'debug-export'
        target.mkdir()
        status = run_godot(args.godot, project, ['--export-debug', 'Windows Desktop', str(target / 'fixture.exe')],
                           output / 'debug-export.log', env)
        if status:
            raise RuntimeError(f'Godot debug export failed ({status})')
        copy_package(target, output / 'debug-missing-leaf', ('leaf.dll',))
    print('Fixture generation complete:', output)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print('Fixture generation incomplete:', exc, file=sys.stderr)
        raise SystemExit(2)
