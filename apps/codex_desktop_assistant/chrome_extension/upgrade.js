// Fixed local update page. Not web-accessible and not an automation capability.
// Chrome still enforces any changed installation permissions itself.
(async()=>{
  await chrome.storage.local.set({autoConnect:true});
  const current=await chrome.tabs.getCurrent(),url=chrome.runtime.getURL('upgrade.html');
  const duplicates=(await chrome.tabs.query({})).filter(tab=>tab.url===url&&tab.id!==current?.id);
  if(duplicates.length)await chrome.tabs.remove(duplicates.map(tab=>tab.id));
  chrome.runtime.reload();
})();
