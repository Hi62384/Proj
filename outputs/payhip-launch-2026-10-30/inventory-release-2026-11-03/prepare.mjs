import fs from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const root=path.dirname(fileURLToPath(import.meta.url));
await fs.mkdir(path.join(root,'authored'),{recursive:true});
const book=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(root,'source/product.xlsx')));
const edits={Calculator:{A1:{value:'Inventory Reorder Planner'},A2:{value:'Review one item: reorder threshold and gap to threshold. Not an optimized order quantity.'},A11:{value:'Gap to reorder threshold'},A15:{value:'Illustrative inputs. Enter all four nonnegative numbers; review supplier and whole-unit constraints.'},B10:{formula:'=IF(COUNT(B5:B8)<>4,"CHECK INPUTS",IF(MIN(B5:B8)<0,"CHECK INPUTS",B5*B6+B7))'},B11:{formula:'=IF(ISNUMBER(B10),MAX(0,B10-B8),"CHECK INPUTS")'}},'Read me':{A1:{value:'Inventory Reorder Planner'},A2:{value:'Single-item reorder threshold and gap. This is not an order-management or forecasting system.'},A4:{value:'2. Enter demand per day, lead time in days, and stock in units.'},A6:{value:'4. Enter all four nonnegative numbers. CHECK INPUTS means missing, text or negative input.'},A7:{value:'5. Fractional inputs are allowed. Review pack sizes, minimum orders and stock on order yourself.'},A9:{value:'Planning aid only. Confirm your assumptions and supplier constraints before ordering.'}}};
for(const [name,cells] of Object.entries(edits))for(const [address,edit] of Object.entries(cells)){
 const r=book.worksheets.getItem(name).getRange(address);
 if(edit.formula)r.formulas=[[edit.formula]];else r.values=[[edit.value]];
}
book.recalculate();
await(await SpreadsheetFile.exportXlsx(book)).save(path.join(root,'authored/Inventory_Reorder_Planner.xlsx'));
await fs.writeFile(path.join(root,'authored/edits.json'),JSON.stringify(edits,null,2));
for(const [sheet,range,file] of [['Calculator','A1:D15','Preview-1.png'],['Read me','A1:A9','Preview-2.png']]){
 const rendered=await book.render({sheetName:sheet,range,scale:1.5});
 await fs.writeFile(path.join(root,'authored',file),new Uint8Array(await rendered.arrayBuffer()));
}
console.log('Authored the targeted Inventory corrections and rendered both changed sheets.');
