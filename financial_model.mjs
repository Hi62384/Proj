/** Reproducible, dependency-free planning model. Run: node financial_model.mjs
 * Edit assumptions.json then rerun. The model makes no requests or transactions.
 * All currencies CAD unless the input key ends in _usd. Values retain precision.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const DIR = path.dirname(fileURLToPath(import.meta.url));
export const assumptions = JSON.parse(fs.readFileSync(path.join(DIR, 'assumptions.json'), 'utf8'));
const sum = values => values.reduce((a,b)=>a+b,0);
const round = (x,n=2) => Math.round((x+Number.EPSILON)*10**n)/10**n;
const assert = (test, message) => {if(!test) throw new Error(message);};
const near = (a,b,where) => assert(Math.abs(a-b)<1e-7, `${where}: ${a} != ${b}`);

export function feeBreakdown(product, orders, revenue, refundRate, chargebackRate, a=assumptions){
  const f=a.fees, fx=a.fx_cad_per_usd, taxBase=revenue*(1+f.assumed_average_checkout_sales_tax_rate);
  const refunds=revenue*refundRate, chargebackLoss=revenue*chargebackRate;
  let platformFee=0,processorFee=0,fixedFee=0,payoutFee=0,fxAllowance=0,disputeFee=0;
  if(product==='assets'){
    platformFee=revenue*f.itch.revenue_share;
    processorFee=taxBase*f.itch.processor_rate;
    fixedFee=orders*f.itch.fixed_usd*fx;
    fxAllowance=Math.max(0,revenue-refunds-chargebackLoss-platformFee-processorFee-fixedFee)*f.itch.fx_payout_contingency_rate;
  }else{
    const rate=f.lemon.base_rate+f.assumed_non_us_buyer_share*f.lemon.non_us_surcharge+f.assumed_paypal_buyer_share*f.lemon.paypal_surcharge+(product==='csv_subscription'?f.lemon.subscription_surcharge:0);
    platformFee=taxBase*rate;
    fixedFee=orders*f.lemon.fixed_usd*fx;
    disputeFee=orders*chargebackRate*f.lemon.dispute_fee_usd*fx;
    const proceeds=Math.max(0,revenue-refunds-chargebackLoss-platformFee-fixedFee-disputeFee);
    payoutFee=proceeds*f.lemon.non_us_bank_payout_rate;
    fxAllowance=(proceeds-payoutFee)*f.lemon.extra_fx_contingency_rate;
  }
  const fees=platformFee+processorFee+fixedFee+payoutFee+fxAllowance+disputeFee;
  const contribution=revenue-refunds-chargebackLoss-fees;
  return {product,orders,revenue,refundRate,chargebackRate,refunds,chargebackLoss,platformFee,processorFee,fixedFee,payoutFee,fxAllowance,disputeFee,fees,contribution};
}

export function runScenario(scenarioName, initialCapital, options={}){
  const a=structuredClone(assumptions), s=structuredClone(a.scenarios[scenarioName]), p=a.prices, c=a.cash_policy,v=a.validation;
  if(options.zeroSales){s.asset_conversion=0;s.localization_conversion=0;s.ad_conversion=0;s.csv_paid_pilots=[0,0,0];s.csv_repeat_use_signals=0;}
  if(options.itchWithholdingRate!==undefined) a.fees.itch.withholding_rate=options.itchWithholdingRate;
  if(options.settlementLagMonths!==undefined) a.settlement.lag_months=options.settlementLagMonths;
  const b=a.budgets[String(initialCapital)];
  assert(b, `Budget ${initialCapital} not configured`);
  let cash=initialCapital,taxReserve=0,taxTarget=0,withheld=0,cumulativeProfit=0,cumulativeEconomic=0,cumulativeHours=0,cumulativeReceipts=0;
  const queue=[]; let assetLive=true,locLive=false,csvLive=false,csvLaunchMonth=null,domainBoughtMonth=null;
  let assetCum=0,locCum=0,paidPilots=0,activeSubs=0,subAcquisitionCarry=0,churnCarry=0;
  let completedAdTests=0,testAdOrders=0,testAdSpend=0,testAdContribution=0,lastGross=0,lastReceipts=0;
  const rows=[]; const skipped=[];
  for(let month=1;month<=a.horizon_months;month++){
    const cashStart=cash,taxStart=taxReserve,receivablesStart=sum(queue.map(q=>q.amount));
    const inflation=(1+a.annual_cost_inflation)**((month-1)/12);
    const events=[];
    let receipts=0,newWithholding=0;
    for(const platform of ['itch','lemon']){
      const eligible=queue.filter(q=>q.platform===platform && q.releaseMonth<=month);
      const eligibleAmount=sum(eligible.map(q=>q.amount));
      const threshold=a.fees[platform].payout_minimum_usd*a.fx_cad_per_usd;
      if(eligibleAmount+1e-9>=threshold){
        const w=platform==='itch'?eligibleAmount*a.fees.itch.withholding_rate:0;
        newWithholding+=w;receipts+=eligibleAmount-w;
        for(const q of eligible) queue.splice(queue.indexOf(q),1);
      }
    }
    cash+=receipts;withheld+=newWithholding;cumulativeReceipts+=receipts;
    // Fund prior tax target before any purchases. A reserve is cash, not expense.
    const priorTaxNeed=Math.max(0,taxTarget-taxReserve);
    const priorTransfer=Math.min(cash,priorTaxNeed);cash-=priorTransfer;taxReserve+=priorTransfer;
    const reserveFloor=month===1?0:Math.max(c.min_discretionary_cash_buffer,lastGross*c.refund_buffer_previous_gross_rate);
    let cashExpenses=0,qaExpense=0,failedExperimentExpense=0,domainExpense=0,softwareExpense=0,hostingExpense=0,adSpend=0;
    let setupHours=0,growthHours=0,organicHours=0,maintenanceHours=0;
    const available=(buffer=true)=>Math.max(0,cash-(buffer?reserveFloor:0)-Math.max(0,taxTarget-taxReserve));
    const buy=(amount, category, buffer=true)=>{
      if(amount<=0) return 0;
      if(available(buffer)+1e-9>=amount){cash-=amount;cashExpenses+=amount;return amount;}
      events.push(`Skipped ${category}: CAD${round(amount)} exceeds settled unreserved cash`);
      skipped.push({month,category,amount});return 0;
    };
    // Only one capital contribution, at time zero. Core downloadable launch is free.
    if(month===1){setupHours+=36;qaExpense+=buy(b.asset_qa,'asset QA',false);events.push('Launch one original asset pack using free storefront/toolchain');}
    if(month===2)setupHours+=24;
    if(month===v.localization_launch_month){
      locLive=true;setupHours+=32;qaExpense+=buy(b.localization_qa*inflation,'localization QA');
      events.push('Launch localization offline licence; 12-month updates obligation, no renewal revenue');
    }
    // Optional domain/software never improves demand mechanically.
    if(month>=2 && month<=6 && domainBoughtMonth===null && available()>=c.domain_annual*inflation && (assetCum>=3||locCum>=3)){
      domainExpense+=buy(c.domain_annual*inflation,'domain'); if(domainExpense)domainBoughtMonth=month;
    }
    if(domainBoughtMonth!==null && month===domainBoughtMonth+12 && (assetLive||locLive))domainExpense+=buy(c.domain_annual*inflation,'domain renewal');
    if((assetLive||locLive) && month>=4 && cash>=500 && lastGross>=150)softwareExpense+=buy(c.optional_software_monthly*inflation,'optional software');
    if(month===7 && (assetCum>=3||locCum>=3)){
      failedExperimentExpense+=buy(b.failed_extension_test*inflation,'failed extension test');growthHours+=12;
      events.push('Retire an unsuccessful asset-extension test: cash and 12 hours spent, zero added sales');
    }
    // Niche pilot research is attempted only after some paid localization validation.
    let pilotOrders=0;
    if(v.csv_pilot_months.includes(month) && locCum>=3){
      const i=v.csv_pilot_months.indexOf(month);
      organicHours+=s.organic_hours_csv_pilots;growthHours+=i===0?12:3;
      pilotOrders=s.csv_paid_pilots[i];paidPilots+=pilotOrders;
      if(pilotOrders)events.push(`${pilotOrders} paid CSV niche pilot(s); no subscription assumed`);
    }
    if(month===9 && paidPilots<v.csv_required_distinct_paid_pilots)events.push('CSV subscription does not launch: fewer than three distinct paid pilots');
    if(!csvLive && month>=v.csv_launch_earliest_month && paidPilots>=v.csv_required_distinct_paid_pilots && s.csv_repeat_use_signals>=v.csv_required_repeat_use_signals){
      if(available()>=c.csv_launch_buffer){csvLive=true;csvLaunchMonth=month;setupHours+=44;events.push('Launch CSV subscription after paid pilot, repeat-use and settled-cash gates');}
      else events.push('Delay CSV launch: operating buffer gate not met');
    }
    // Whole subscriptions with deterministic carry-forward; retention is not revenue from the offline licence.
    const subsStart=activeSubs;
    let newSubscribers=0,churnedSubscribers=0;
    if(csvLive){
      churnCarry+=activeSubs*s.csv_monthly_churn;
      churnedSubscribers=Math.min(activeSubs,Math.floor(churnCarry+1e-9));churnCarry-=churnedSubscribers;
      activeSubs-=churnedSubscribers;
      const age=month-csvLaunchMonth;
      const proposed=s.csv_new_subscribers_initial+age*s.csv_new_subscribers_growth;
      // Acquisition tapers to zero at the niche-cap; churn frees capacity.
      subAcquisitionCarry+=proposed*Math.max(0,1-activeSubs/s.csv_customer_cap);
      newSubscribers=Math.min(s.csv_customer_cap-activeSubs,Math.floor(subAcquisitionCarry+1e-9));subAcquisitionCarry-=newSubscribers;
      activeSubs+=newSubscribers;
      hostingExpense=buy((c.csv_hosting_monthly+c.csv_hosting_per_subscriber*activeSubs)*inflation,'CSV hosting',false);
      if(hostingExpense===0){
        events.push('CSV suspended before billing: insufficient settled hosting cash');
        activeSubs=0;newSubscribers=0;csvLive=false;
      }else organicHours+=s.organic_hours_csv_live;
    }
    // Ad tests occur only after two prior tool sales. Scale only after all test spends are recovered by first-order contribution.
    const adsValidated=completedAdTests>=v.max_initial_ad_tests && testAdOrders>=v.paid_ad_min_test_orders && testAdContribution>=testAdSpend;
    let adTarget=0;
    if(locLive && month>=4 && locCum>=v.paid_ad_min_previous_localization_orders){
      if(completedAdTests<v.max_initial_ad_tests)adTarget=b.ad_test*inflation;
      else if(adsValidated)adTarget=Math.min(c.ad_scale_monthly_cap*inflation,c.reinvestment_settled_receipts_rate*lastReceipts);
    }
    // Never partially fund a planned test; a scaled campaign can be capped by cash.
    if(completedAdTests>=v.max_initial_ad_tests)adTarget=Math.min(adTarget,available());
    if(adTarget>=10)adSpend=buy(adTarget,'paid acquisition');
    const currentCpc=s.ad_cpc*(1+s.monthly_paid_channel_cpc_growth)**(month-1)*inflation;
    const paidVisits=adSpend/currentCpc;
    const paidOrders=locLive?Math.floor(paidVisits*s.ad_conversion+1e-9):0;
    const paidContribution=feeBreakdown('localization',paidOrders,paidOrders*p.localization,s.localization_refund_rate,s.chargeback_rate,a).contribution;
    if(adSpend>0 && completedAdTests<v.max_initial_ad_tests){completedAdTests++;testAdOrders+=paidOrders;testAdSpend+=adSpend;testAdContribution+=paidContribution;}
    const decay=(1-s.post_year_one_monthly_traffic_decay)**Math.max(0,month-12);
    const assetVisits=assetLive?Math.floor((s.asset_visits[month-1]??Math.min(s.asset_traffic_cap,s.asset_initial_visits+(month-1)*s.asset_monthly_visit_gain))*decay):0;
    const locAge=month-v.localization_launch_month;
    const locVisits=locLive?Math.floor(Math.min(s.localization_traffic_cap,s.localization_initial_visits+locAge*s.localization_monthly_visit_gain)*decay):0;
    const assetOrders=assetLive?Math.floor(assetVisits*s.asset_conversion+1e-9):0;
    const locOrganicOrders=locLive?Math.floor(locVisits*s.localization_conversion+1e-9):0;
    const locOrders=locOrganicOrders+paidOrders;
    const products=[
      feeBreakdown('assets',assetOrders,assetOrders*p.assets,s.asset_refund_rate,s.chargeback_rate,a),
      feeBreakdown('localization',locOrders,locOrders*p.localization,s.localization_refund_rate,s.chargeback_rate,a),
      feeBreakdown('csv_pilot',pilotOrders,pilotOrders*p.csv_paid_pilot,s.subscription_refund_rate,s.chargeback_rate,a),
      feeBreakdown('csv_subscription',activeSubs,activeSubs*p.csv_subscription,s.subscription_refund_rate,s.chargeback_rate,a)
    ];
    const grossRevenue=sum(products.map(z=>z.revenue)),refunds=sum(products.map(z=>z.refunds)),chargebackLoss=sum(products.map(z=>z.chargebackLoss)),fees=sum(products.map(z=>z.fees));
    const contribution=sum(products.map(z=>z.contribution));
    const pretaxProfit=contribution-cashExpenses;
    // Receivables already net of refund/dispute and fee allowances, not spendable yet.
    for(const z of products){if(z.contribution>0)queue.push({platform:z.product==='assets'?'itch':'lemon',amount:z.contribution,releaseMonth:month+a.settlement.lag_months});}
    assetCum+=assetOrders;locCum+=locOrders;
    const lateEffort=month>12?0.7:1;
    if(assetLive)organicHours+=s.organic_hours_assets*lateEffort;
    if(locLive)organicHours+=s.organic_hours_localization*lateEffort;
    if(month>=4 && (assetLive||locLive))growthHours+=s.growth_hours*(month>12?0.5:1);
    if(assetLive)maintenanceHours+=0.8+0.05*assetOrders;
    else if(assetCum>0 && month<=12)maintenanceHours+=0.35;
    if(locLive)maintenanceHours+=1.5+0.12*locOrders;
    // 12-month update obligations continue even if new tool sales cease.
    else if(locCum>0 && rows.slice(-12).some(r=>r.localization_orders>0))maintenanceHours+=1.5;
    if(csvLive)maintenanceHours+=2.5+0.12*activeSubs;
    maintenanceHours+=(assetLive||locLive||csvLive)?1.25:0.25; // bookkeeping/monitoring, not acquisition
    const paidAcquisitionHours=adSpend>0?1.5+adSpend/500:0;
    const ownerHours=setupHours+growthHours+organicHours+paidAcquisitionHours+maintenanceHours;
    const economicProfit=pretaxProfit-ownerHours*a.owner_hourly_value;
    cumulativeProfit+=pretaxProfit;cumulativeEconomic+=economicProfit;cumulativeHours+=ownerHours;
    taxTarget=Math.max(0,cumulativeProfit*a.income_tax_reserve_rate);
    if(taxReserve>taxTarget){cash+=taxReserve-taxTarget;taxReserve=taxTarget;}
    else{const t=Math.min(cash,taxTarget-taxReserve);cash-=t;taxReserve+=t;}
    const receivablesEnd=sum(queue.map(q=>q.amount));
    if(month===v.asset_retire_review_month && assetCum<v.asset_min_cumulative_orders){assetLive=false;events.push('Stop asset acquisition after failed paid-demand review');}
    if(month===v.localization_retire_review_month && locCum<v.localization_min_cumulative_orders){locLive=false;events.push('Stop localization acquisition after failed paid-demand review');}
    const allOrders=assetOrders+locOrders+pilotOrders+activeSubs;
    const row={
      scenario:scenarioName,initial_capital:initialCapital,month,
      asset_organic_visits:assetVisits,asset_conversion:s.asset_conversion,asset_orders:assetOrders,
      localization_organic_visits:locVisits,localization_conversion:s.localization_conversion,localization_organic_orders:locOrganicOrders,localization_paid_orders:paidOrders,localization_orders:locOrders,
      paid_visits:paidVisits,paid_conversion:s.ad_conversion,paid_cpc:currentCpc,paid_cac:paidOrders?adSpend/paidOrders:null,
      csv_pilot_orders:pilotOrders,csv_paid_pilots_cumulative:paidPilots,csv_subscribers_start:subsStart,csv_new_subscribers:newSubscribers,csv_churned_subscribers:churnedSubscribers,csv_active_subscribers:activeSubs,csv_launch_month:csvLaunchMonth,
      products,gross_revenue:grossRevenue,refunds,chargeback_losses:chargebackLoss,fees,net_sales_after_refunds:grossRevenue-refunds-chargebackLoss,contribution,
      qa_expense:qaExpense,failed_experiment_expense:failedExperimentExpense,domain_expense:domainExpense,software_expense:softwareExpense,hosting_expense:hostingExpense,api_expense:0,ad_spend:adSpend,
      cash_operating_expenses:cashExpenses,total_expenses:refunds+chargebackLoss+fees+cashExpenses,pretax_profit:pretaxProfit,
      growth_reinvestment_expense:qaExpense+failedExperimentExpense+adSpend,
      setup_hours:setupHours,growth_hours:growthHours,organic_acquisition_hours:organicHours,paid_acquisition_hours:paidAcquisitionHours,maintenance_hours:maintenanceHours,owner_hours:ownerHours,owner_hours_per_week:ownerHours/(52/12),maintenance_hours_per_week:maintenanceHours/(52/12),owner_time_value:ownerHours*a.owner_hourly_value,economic_profit:economicProfit,
      cash_start:cashStart,settled_receipts:receipts,withholding_current:newWithholding,cumulative_withholding:withheld,cash_operating_flow:receipts-cashExpenses,tax_reserve_transfer:taxReserve-taxStart,
      tax_reserve_target:taxTarget,tax_reserve_held:taxReserve,tax_reserve_unfunded:Math.max(0,taxTarget-taxReserve),cash_end:cash,unreserved_spendable_cash:Math.max(0,cash-reserveFloor-Math.max(0,taxTarget-taxReserve)),refund_operating_buffer_target:reserveFloor,
      receivables_start:receivablesStart,receivables_end:receivablesEnd,cumulative_pretax_profit:cumulativeProfit,cumulative_economic_profit:cumulativeEconomic,cumulative_owner_hours:cumulativeHours,cumulative_settled_receipts:cumulativeReceipts,
      organic_economic_cac:(assetOrders+locOrganicOrders+pilotOrders+newSubscribers)?organicHours*a.owner_hourly_value/(assetOrders+locOrganicOrders+pilotOrders+newSubscribers):null,
      paid_tests_completed:completedAdTests,paid_test_orders:testAdOrders,paid_tests_spend:testAdSpend,paid_tests_contribution:testAdContribution,paid_channel_validated:completedAdTests>=v.max_initial_ad_tests&&testAdOrders>=v.paid_ad_min_test_orders&&testAdContribution>=testAdSpend,events
    };
    // Independent accounting identities within each path; fail instead of masking errors.
    near(grossRevenue-row.total_expenses,pretaxProfit,'P&L');
    near(cashStart+receipts-cashExpenses-row.tax_reserve_transfer,cash,'cash bridge');
    near(receivablesStart+contribution-receipts-newWithholding,receivablesEnd,'receivables bridge');
    near(cash+taxReserve+receivablesEnd+withheld,initialCapital+cumulativeProfit,'balance sheet');
    near(sum([qaExpense,failedExperimentExpense,domainExpense,softwareExpense,hostingExpense,adSpend]),cashExpenses,'expense components');
    assert(cash>=-1e-7 && taxReserve>=-1e-7,'No hidden borrowing');
    assert(activeSubs<=s.csv_customer_cap,'Customer cap');
    assert(!csvLaunchMonth||paidPilots>=v.csv_required_distinct_paid_pilots,'Pilot validation');
    assert(allOrders>=0 && Number.isInteger(allOrders),'Whole orders');
    rows.push(row);lastGross=grossRevenue;lastReceipts=receipts;
  }
  return {scenario:scenarioName,initial_capital:initialCapital,options,rows,skipped_spending:skipped,ending:rows.at(-1)};
}

export function generateResults(){
  const paths=[];
  for(const scenario of Object.keys(assumptions.scenarios)) for(const budget of assumptions.initial_capital_cases) paths.push(runScenario(scenario,budget));
  const summaries=paths.flatMap(x=>x.rows.filter(r=>assumptions.milestone_months.includes(r.month)).map(r=>({
    scenario:r.scenario,initial_capital:r.initial_capital,month:r.month,gross_revenue:r.gross_revenue,total_expenses:r.total_expenses,pretax_profit:r.pretax_profit,economic_profit:r.economic_profit,owner_hours:r.owner_hours,setup_hours:r.setup_hours,growth_hours:r.growth_hours,organic_acquisition_hours:r.organic_acquisition_hours,paid_acquisition_hours:r.paid_acquisition_hours,maintenance_hours:r.maintenance_hours,
    settled_receipts:r.settled_receipts,cash_operating_flow:r.cash_operating_flow,cash_end:r.cash_end,tax_reserve_held:r.tax_reserve_held,tax_reserve_unfunded:r.tax_reserve_unfunded,receivables_end:r.receivables_end,cumulative_pretax_profit:r.cumulative_pretax_profit,cumulative_economic_profit:r.cumulative_economic_profit,cumulative_owner_hours:r.cumulative_owner_hours,asset_orders:r.asset_orders,localization_orders:r.localization_orders,csv_active_subscribers:r.csv_active_subscribers,ad_spend:r.ad_spend,growth_reinvestment_expense:r.growth_reinvestment_expense
  })));
  const stressTests={
    zero_sales:assumptions.initial_capital_cases.map(b=>runScenario('base',b,{zeroSales:true})),
    itch_30_percent_withholding:assumptions.initial_capital_cases.map(b=>runScenario('base',b,{itchWithholdingRate:0.3})),
    two_month_settlement_delay:assumptions.initial_capital_cases.map(b=>runScenario('base',b,{settlementLagMonths:2}))
  };
  const unitEconomics={};
  for(const name of Object.keys(assumptions.scenarios)){
    const s=assumptions.scenarios[name];unitEconomics[name]={};
    for(const product of ['assets','localization','csv_subscription']){
      const price=assumptions.prices[product],r=product==='assets'?s.asset_refund_rate:product==='localization'?s.localization_refund_rate:s.subscription_refund_rate;
      const f=feeBreakdown(product,1,price,r,s.chargeback_rate);
      unitEconomics[name][product]={...f,first_order_cash_cac_ceiling:f.contribution,contribution_margin:f.contribution/price};
    }
  }
  const checks={paths:paths.length,monthly_rows:sum(paths.map(p=>p.rows.length)),summary_rows:summaries.length,stress_paths:sum(Object.values(stressTests).map(x=>x.length)),stress_monthly_rows:sum(Object.values(stressTests).flat().map(p=>p.rows.length)),negative_monthly_pretax_rows:paths.flatMap(p=>p.rows).filter(r=>r.pretax_profit<0).length,negative_monthly_economic_rows:paths.flatMap(p=>p.rows).filter(r=>r.economic_profit<0).length,identities:'All rows pass profit, cash bridge, receivables bridge, balance sheet, expense decomposition, nonnegative cash and validation gate tests.'};
  assert(checks.paths===12 && checks.monthly_rows===288 && checks.summary_rows===60,'Required case count');
  for(const z of stressTests.zero_sales){assert(z.rows.every(r=>r.gross_revenue===0),'Zero-sales test');assert(z.ending.cash_end>=0,'Zero-sales liquidity');}
  const results={model_version:assumptions.model_version,as_of:assumptions.as_of,currency:'CAD',disclaimer:assumptions.status,assumptions_file:'assumptions.json',unit_economics:unitEconomics,summary_rows:summaries,paths,stress_tests:stressTests,checks};
  return results;
}

if(process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const results=generateResults();
 fs.writeFileSync(path.join(DIR,'financial_results.json'),JSON.stringify(results,null,2)+'\n');
 fs.writeFileSync(path.join(DIR,'financial_summary.json'),JSON.stringify(results.summary_rows,null,2)+'\n');
 console.log(JSON.stringify(results.checks,null,2));
 console.log('\nMilestones: CAD monthly pretax operating profit, not take-home pay');
 for(const name of Object.keys(assumptions.scenarios)) for(const b of assumptions.initial_capital_cases){
  const rows=results.summary_rows.filter(r=>r.scenario===name&&r.initial_capital===b);
  console.log(name,b,rows.map(r=>`M${r.month} ${round(r.pretax_profit)} (revenue ${round(r.gross_revenue)}; hours ${round(r.owner_hours,1)})`).join(' | '));
 }
}
