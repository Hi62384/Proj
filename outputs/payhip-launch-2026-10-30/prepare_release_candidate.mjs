// Targeted edits to the existing print-fixed workbooks, not a regenerated design.
import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const root=path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/,'$1'));
const output=path.join(root,'verification-2026-11-01','authored');await fs.mkdir(output,{recursive:true});
const settings='IF(COUNT(SETTINGS!$B$10:$B$18)=9,AND(MIN(SETTINGS!$B$10:$B$18)>=0,SETTINGS!$B$14+SETTINGS!$B$15<1,SETTINGS!$B$17>0,SETTINGS!$B$18<=1,UPPER(TRIM(SETTINGS!$B$22))="CAD"),FALSE)';
const logSettings='IF(AND(COUNT(SETTINGS!$B$10:$B$12)=3,ISNUMBER(SETTINGS!$B$15)),AND(MIN(SETTINGS!$B$10:$B$12)>=0,SETTINGS!$B$15>=0,SETTINGS!$B$15<=1),FALSE)';
const numeric=(cells)=>'AND('+cells.map(c=>'OR('+c+'="",ISNUMBER('+c+'))').join(',')+')';
const service=(name,hours)=>`AND(ISNUMBER(VLOOKUP(${name},SERVICES!$A$9:$C$15,3,FALSE)),VLOOKUP(${name},SERVICES!$A$9:$C$15,3,FALSE)>=0,IF(${hours}="",AND(ISNUMBER(VLOOKUP(${name},SERVICES!$A$9:$C$15,2,FALSE)),VLOOKUP(${name},SERVICES!$A$9:$C$15,2,FALSE)>0),TRUE))`;
const changes={};const f=(sheet,cell,formula)=>{(changes[sheet]??={})[cell]={formula:'='+formula};};
f('QUICK QUOTE','F27',`IF(B11="","SELECT SERVICE",IF(COUNTIF(SERVICES!$A$9:$A$15,B11)<>1,"INVALID SERVICE",IF(NOT(${settings}),"CHECK INPUTS",IF(NOT(AND(ISNUMBER(B12),${numeric(['B13','B14','B15','B16','B17','B18','B19'])},${service('B11','B13')})),"CHECK INPUTS",IF(OR(B12<1,B12<>INT(B12),AND(B13<>"",B13<=0),B14<0,B15<0,B16<0,B17<0,B18<0,AND(B19<>"",OR(B19<0,B19>1))),"CHECK INPUTS",IF(SETTINGS!$B$23<>"READY","REVIEW SETTINGS","READY TO REVIEW"))))))`);
for(let r=10;r<=34;r++){
 f('JOB SCENARIOS','Q'+r,`IF(A${r}="","",IF(COUNTIF(SERVICES!$A$9:$A$15,B${r})<>1,"CHECK SERVICE",IF(NOT(${settings}),"CHECK INPUTS",IF(NOT(AND(ISNUMBER(C${r}),${numeric(['D','E','F','G','H','I'].map(c=>c+r))},${service('B'+r,'D'+r)})),"CHECK INPUTS",IF(OR(C${r}<1,C${r}<>INT(C${r}),AND(D${r}<>"",D${r}<=0),E${r}<0,F${r}<0,G${r}<0,H${r}<0,I${r}<0),"CHECK INPUTS",IF(SETTINGS!$B$23<>"READY","REVIEW SETTINGS","READY"))))))`);
 const valid=`IF(COUNT(D${r}:I${r})=6,AND(MIN(D${r}:I${r})>=0,${logSettings}),FALSE)`;
 const expressions={J:`ROUND(F${r}*SETTINGS!$B$10+G${r}+H${r}*SETTINGS!$B$11+I${r}+SETTINGS!$B$12+E${r}*SETTINGS!$B$15,2)`,K:`E${r}-J${r}`,L:`IF(E${r}>0,K${r}/E${r},0)`,M:`E${r}-D${r}`};
 for(const [col,expr]of Object.entries(expressions))f('JOB LOG',col+r,`IF(A${r}="","",IF(NOT(${valid}),"CHECK INPUTS",${expr}))`);
}
const badScenarios='COUNTIF(\'JOB SCENARIOS\'!Q10:Q34,"CHECK INPUTS")+COUNTIF(\'JOB SCENARIOS\'!Q10:Q34,"CHECK SERVICE")>0';
for(const [c,expr]of Object.entries({E9:"SUM('JOB SCENARIOS'!M10:M34)",H9:"SUM('JOB SCENARIOS'!O10:O34)",K9:'IF(E9>0,H9/E9,0)'}))f('OVERVIEW',c,`IF(${badScenarios},"CHECK SCENARIOS",${expr})`);
for(const [c,expr]of Object.entries({E15:"SUM('JOB LOG'!E10:E34)",H15:"SUM('JOB LOG'!K10:K34)",K15:'IF(E15>0,H15/E15,0)'}))f('OVERVIEW',c,`IF(COUNTIF('JOB LOG'!J10:J34,"CHECK INPUTS")>0,"CHECK JOB LOG",${expr})`);
changes.SETTINGS={A19:{value:'Suggested quote validity (days)'},C19:{value:'Manual guidance; no automatic expiry is printed on CLIENT QUOTE.'},A22:{value:'Currency (CAD only)'},C22:{value:'CAD labels only. Other currencies are not supported.'}};
for(const filename of ['Cleaning_Pricing_Calculator.xlsx','Cleaning_Pricing_Calculator_FICTIONAL_DEMO.xlsx']){
 const book=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(root,'print-review-copies',filename)));
 for(const [sheet,cells]of Object.entries(changes))for(const [cell,edit]of Object.entries(cells)){
  const range=book.worksheets.getItem(sheet).getRange(cell);if(edit.formula)range.formulas=[[edit.formula]];else range.values=[[edit.value]];
 }
 book.worksheets.getItem('QUICK QUOTE').getRange('B11').dataValidation={rule:{type:'list',formula1:'ServiceNames'}};
 book.worksheets.getItem('JOB SCENARIOS').getRange('B10:B34').dataValidation={rule:{type:'list',formula1:'ServiceNames'}};
 book.recalculate();
 const result=await SpreadsheetFile.exportXlsx(book);await result.save(path.join(output,filename));
 console.log('Authored targeted input guards and service dropdowns: '+filename);
}
await fs.writeFile(path.join(output,'changes.json'),JSON.stringify(changes,null,2));
