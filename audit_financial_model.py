"""Independent Python audit of JSON outputs; does not call the JavaScript model.
Run after node financial_model.mjs: python audit_financial_model.py
"""
import json, math
from pathlib import Path
D=Path(__file__).resolve().parent
A=json.loads((D/'assumptions.json').read_text()); R=json.loads((D/'financial_results.json').read_text())
checks=0

def close(x,y,label):
    global checks
    if not math.isclose(x,y,rel_tol=1e-10,abs_tol=1e-7): raise AssertionError(f'{label}: {x} != {y}')
    checks+=1

def truth(test,label):
    global checks
    if not test:raise AssertionError(label)
    checks+=1

paths=R['paths']+sum(R['stress_tests'].values(),[])
for path in paths:
    prev=None
    cumulative_profit=0;cumulative_hours=0;cumulative_economic=0
    for row in path['rows']:
        expected_contribution=0; expected_fees=0; expected_refunds=0; expected_cb=0; gross=0
        for z in row['products']:
            product=z['product']; n=z['orders']; price=A['prices'][product if product!='csv_pilot' else 'csv_paid_pilot']
            rev=n*price; gross+=rev;close(rev,z['revenue'],'orders x price')
            refund=rev*z['refundRate']; loss=rev*z['chargebackRate']
            expected_refunds+=refund;expected_cb+=loss
            close(refund,z['refunds'],'refunds');close(loss,z['chargebackLoss'],'disputed revenue')
            f=A['fees'];taxbase=rev*(1+f['assumed_average_checkout_sales_tax_rate']);fx=A['fx_cad_per_usd']
            if product=='assets':
                platform=rev*f['itch']['revenue_share'];processor=taxbase*f['itch']['processor_rate'];fixed=n*f['itch']['fixed_usd']*fx
                payout=0; dispute=0; allowance=max(0,rev-refund-loss-platform-processor-fixed)*f['itch']['fx_payout_contingency_rate']
            else:
                lf=f['lemon'];rate=lf['base_rate']+f['assumed_non_us_buyer_share']*lf['non_us_surcharge']+f['assumed_paypal_buyer_share']*lf['paypal_surcharge']+(lf['subscription_surcharge'] if product=='csv_subscription' else 0)
                platform=taxbase*rate;processor=0;fixed=n*lf['fixed_usd']*fx;dispute=n*z['chargebackRate']*lf['dispute_fee_usd']*fx
                proceeds=max(0,rev-refund-loss-platform-fixed-dispute);payout=proceeds*lf['non_us_bank_payout_rate'];allowance=(proceeds-payout)*lf['extra_fx_contingency_rate']
            for name,value in [('platformFee',platform),('processorFee',processor),('fixedFee',fixed),('disputeFee',dispute),('payoutFee',payout),('fxAllowance',allowance)]:close(value,z[name],name)
            fees=platform+processor+fixed+dispute+payout+allowance
            contribution=rev-refund-loss-fees
            close(fees,z['fees'],'product fees');close(contribution,z['contribution'],'product contribution')
            expected_contribution+=contribution;expected_fees+=fees
        close(gross,row['gross_revenue'],'gross total')
        close(expected_fees,row['fees'],'total fees');close(expected_refunds,row['refunds'],'total refunds');close(expected_cb,row['chargeback_losses'],'total disputes')
        expenses=sum(row[k] for k in ['qa_expense','failed_experiment_expense','domain_expense','software_expense','hosting_expense','api_expense','ad_spend'])
        close(expenses,row['cash_operating_expenses'],'cash expense categories')
        profit=expected_contribution-expenses
        close(profit,row['pretax_profit'],'independent profit')
        close(gross-row['total_expenses'],profit,'gross less all costs')
        close(row['cash_start']+row['settled_receipts']-expenses-row['tax_reserve_transfer'],row['cash_end'],'cash bridge')
        close(row['receivables_start']+expected_contribution-row['settled_receipts']-row['withholding_current'],row['receivables_end'],'AR bridge')
        hours=sum(row[k] for k in ['setup_hours','growth_hours','organic_acquisition_hours','paid_acquisition_hours','maintenance_hours'])
        close(hours,row['owner_hours'],'all owner hours');close(profit-hours*A['owner_hourly_value'],row['economic_profit'],'economic profit')
        cumulative_profit+=profit;cumulative_hours+=hours;cumulative_economic+=profit-hours*A['owner_hourly_value']
        close(cumulative_profit,row['cumulative_pretax_profit'],'cumulative profit');close(cumulative_hours,row['cumulative_owner_hours'],'cumulative hours');close(cumulative_economic,row['cumulative_economic_profit'],'cumulative economic profit')
        close(row['cash_end']+row['tax_reserve_held']+row['receivables_end']+row['cumulative_withholding'],path['initial_capital']+cumulative_profit,'independent balance sheet')
        close(max(0,cumulative_profit*A['income_tax_reserve_rate']),row['tax_reserve_target'],'tax reserve target')
        truth(row['cash_end']>=-1e-7,'nonnegative cash')
        truth(row['csv_active_subscribers']>=0 and row['csv_active_subscribers']%1==0,'whole customers')
        if row['csv_launch_month'] is not None:truth(row['csv_paid_pilots_cumulative']>=3,'paid-pilot gate')
        if prev:
            close(prev['cash_end'],row['cash_start'],'cash continuity');close(prev['receivables_end'],row['receivables_start'],'AR continuity')
            close(prev['csv_active_subscribers']-row['csv_churned_subscribers']+row['csv_new_subscribers'],row['csv_active_subscribers'],'subscriber rollforward')
        else:close(path['initial_capital'],row['cash_start'],'only initial contribution')
        prev=row
    truth(len(path['rows'])==24,'24 month rows')
truth(len(R['summary_rows'])==60,'60 summary rows')
for x in R['summary_rows']:
    y=next(p for p in R['paths'] if p['scenario']==x['scenario'] and p['initial_capital']==x['initial_capital'])['rows'][x['month']-1]
    for k,v in x.items():
        if isinstance(v,(int,float)):close(v,y[k],'summary reconciles to monthly ledger')
        else:truth(v==y[k],'summary text')
for p in R['stress_tests']['zero_sales']:
    truth(all(r['gross_revenue']==0 for r in p['rows']),'zero sale path has no revenue')
    truth(p['ending']['cash_end']>=0,'zero sale no borrowing')
report={'status':'PASS','independent_runtime':'Python standard library; JavaScript not imported','assertions_passed':checks,'paths_audited':len(paths),'rows_audited':sum(len(p['rows']) for p in paths),'notes':['Recomputed every product fee/refund, profit, expense sum, labour value, cash bridge, receivable bridge, balance-sheet identity and subscriber roll-forward.','Summary rows independently reconciled to original monthly rows.','Arithmetic correctness does not validate assumed demand, platform eligibility, jurisdictional costs or commercial viability.']}
(D/'financial_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
