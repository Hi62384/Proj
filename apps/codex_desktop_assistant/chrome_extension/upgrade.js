// Fixed local update page. Not web-accessible and not an automation capability.
// Chrome still enforces any changed installation permissions itself.
chrome.storage.local.set({autoConnect:true}).then(()=>chrome.runtime.reload());
