import {Workbook} from '@oai/artifact-tool';
const wb=Workbook.create();wb.worksheets.add('Review');
console.log(wb.help('worksheet page print layout',{search:'pageLayout|pageSetup|printArea|fitTo|print',include:'index,notes',maxChars:3500}).ndjson);
