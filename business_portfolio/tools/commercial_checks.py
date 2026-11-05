#!/usr/bin/env python3
"""Offline commercial arithmetic/record checks. No network or transaction authority.
Python 3.10+; standard library only. All money in a request must already be CAD.
"""
from __future__ import annotations
import argparse
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import json
from pathlib import Path
import sys

class CommercialError(ValueError):
    pass

def number(value, name='number') -> Decimal:
    if isinstance(value,bool) or value is None:
        raise CommercialError(f'{name}: an explicit finite nonnegative number is required')
    try:
        x=Decimal(str(value))
    except (InvalidOperation,ValueError,TypeError) as e:
        raise CommercialError(f'{name}: invalid number') from e
    if not x.is_finite() or x<0:
        raise CommercialError(f'{name}: an explicit finite nonnegative number is required')
    return x

def fraction(value,name):
    x=number(value,name)
    if x>=1:raise CommercialError(f'{name}: must be below one')
    return x

def contribution(price, fee_fraction, refund_fraction, cash_cost=0, fixed_fee=0):
    p=number(price,'price');f=fraction(fee_fraction,'fee');r=fraction(refund_fraction,'refund reserve')
    if f+r>=1:raise CommercialError('Combined fee and reserve must be below one')
    return p*(1-f-r)-number(cash_cost,'cash cost')-number(fixed_fee,'fixed fee')

def quote_floor(hours, hourly_target, cash_cost, fee_fraction, refund_fraction=0):
    h=number(hours,'hours');w=number(hourly_target,'hourly target');c=number(cash_cost,'cash cost')
    f=fraction(fee_fraction,'fee');r=fraction(refund_fraction,'refund reserve')
    if f+r>=1:raise CommercialError('Combined fee and reserve must be below one')
    return (h*w+c)/(1-f-r)

def round_money(x):return x.quantize(Decimal('.01'),rounding=ROUND_HALF_UP)

def validate_record(record):
    if record.get('commercial_revision')!=2:return
    ident=record.get('id','unknown')
    budget=record.get('owner_budget')
    if not isinstance(budget,dict):raise CommercialError(f'{ident}: missing budget')
    if budget.get('currency')!='CAD':raise CommercialError(f'{ident}: budget must use CAD')
    ceiling=number(budget.get('hard_ceiling'),'hard ceiling')
    if ceiling>100:raise CommercialError(f'{ident}: hard ceiling exceeds CAD100')
    for field in ['preferred_upfront','planned_upfront','authorized_spend','optional_total_ceiling']:
        if number(budget.get(field),field)>ceiling:raise CommercialError(f'{ident}: {field} exceeds ceiling')
    if number(budget.get('owner_recurring_monthly'),'monthly recurring')!=0:
        raise CommercialError(f'{ident}: recurring owner cost requires an explicitly revised plan, not this zero-recurring policy')
    env=budget.get('optional_all_in_envelope')
    if not isinstance(env,dict):raise CommercialError(f'{ident}: missing optional envelope')
    total=sum((number(v,k) for k,v in env.items()),Decimal(0))
    if total>number(budget['optional_total_ceiling']) or total>ceiling:
        raise CommercialError(f'{ident}: optional envelope exceeds its total or ceiling')
    if number(budget['authorized_spend'])>0 and not budget.get('approval_ref'):
        raise CommercialError(f'{ident}: positive authorization requires an approval reference')
    if record.get('marketing_execution_authorized') and not record.get('marketing_approval_ref'):
        raise CommercialError(f'{ident}: marketing authorization requires an approval reference')
    for field in ['launch_gate','marketing_lane','success_probability']:
        if not record.get(field):raise CommercialError(f'{ident}: missing {field}')
    if record.get('record_type')=='bundled_component':
        if total or not record.get('parent_project'):raise CommercialError(f'{ident}: component needs parent and zero separate envelope')
    for scenario in record.get('economics_scenarios',[]):
        net=contribution(scenario['price_cad'],scenario['combined_fee_fraction'],scenario['refund_reserve_fraction'],scenario['allocated_cash_cost_cad'])
        if abs(round_money(net)-Decimal(str(scenario['contribution_before_owner_labor_cad'])))>Decimal('.01'):
            raise CommercialError(f'{ident}: scenario contribution mismatch')
        h=number(scenario['total_owner_hours'],'total hours')
        if not h:raise CommercialError(f'{ident}: effective hourly figure needs nonzero hours')
        if abs(round_money(net/h)-Decimal(str(scenario['effective_cad_per_owner_hour'])))>Decimal('.01'):
            raise CommercialError(f'{ident}: hourly scenario mismatch')

def validate_spend_request(request):
    """Check one proposed commitment, not actual authorization or available bank cash."""
    if request.get('currency')!='CAD':raise CommercialError('Convert the full committed amount to CAD with verified tax/FX first')
    if request.get('costs_verified') is not True:raise CommercialError('Unknown/unverified costs block the request')
    if not request.get('approval_ref'):raise CommercialError('No approval reference; no purchase authorized')
    if request.get('auto_renewal') is not False:raise CommercialError('Auto-renewal must be explicitly off')
    fields=['already_spent','existing_commitments','proposed_cost','tax_and_fx','new_noncancelable_commitments']
    total=sum((number(request.get(k),k) for k in fields),Decimal(0))
    approved=number(request.get('approved_total'),'approved total')
    if approved>100 or total>100:raise CommercialError('Cumulative launch commitments exceed CAD100')
    if total>approved:raise CommercialError('Cumulative commitments exceed the actual approved total')
    return total

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    group=ap.add_mutually_exclusive_group(required=True)
    group.add_argument('--portfolio',type=Path)
    group.add_argument('--request',type=Path)
    args=ap.parse_args()
    try:
        if args.portfolio:
            import build_browser
            d=build_browser.load_portfolio(args.portfolio)
            for r in d['records']:validate_record(r)
            print(f"Checked {len(d['records'])} commercial records and explicit scenarios. No actual sales, prices, bank balances or external permissions verified.")
        else:
            r=json.loads(args.request.read_text(encoding='utf-8'))
            total=validate_spend_request(r)
            print(f'Arithmetic passes: CAD{total}. This does not independently verify the claimed approval or authorize a transaction.')
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print('Commercial check blocked: '+str(exc),file=sys.stderr);return 1
    return 0
if __name__=='__main__':raise SystemExit(main())
