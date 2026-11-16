#!/usr/bin/env python3
"""Reproduce summary-statistic calculations and six companion charts.

Important: published-summary reconstructions, NOT participant-level replications.
Run: python reproduce_oral_sex_figures.py
All inputs and outputs are relative to the location of this script.
"""
from __future__ import annotations
import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import fisher_exact, norm

ROOT = Path(__file__).resolve().parent
TEAL = '#668f99'
LIGHT = '#a7bdc5'
INK = '#1c3546'
GREY = '#5f6f78'
DPI = 170


def rows(name):
    with (ROOT / name).open(encoding='utf-8', newline='') as file:
        return list(csv.DictReader(file))


def number_map(name, key='key'):
    return {row[key]: float(row['value']) for row in rows(name)}


def fisher_z_ci(r: float, n: int, alpha: float = 0.05) -> tuple[float, float]:
    if n <= 3 or not (-1 < r < 1):
        raise ValueError('Fisher-z interval requires n>3 and -1<r<1')
    z = math.atanh(r)
    half_width = norm.ppf(1-alpha/2) / math.sqrt(n-3)
    return math.tanh(z-half_width), math.tanh(z+half_width)


def max_sample_sd(n: int, lower: float, upper: float) -> float:
    """Upper bound for integer n and bounded interval; tight for even n here."""
    if n <= 1:
        raise ValueError('n must be greater than 1')
    return (upper-lower)/2 * math.sqrt(n/(n-1))


def scenarios():
    d = number_map('datepsych_2023_reported.csv')
    women_n = int(d['women_n'])
    men_n = int(d['men_n'])
    women_yes = int(d['oral_partners_more_women'])
    male_counts = [
        ('If oral-greater total were 45', 33),
        ('If oral-greater total were 57', 45),
        ('If reported 12.7% were correct', 57),
    ]
    answer = []
    for name, men_yes in male_counts:
        # scipy Fisher's exact: two-sided means probability-ordering definition.
        odds, p = fisher_exact([[women_yes, women_n-women_yes],
                                [men_yes, men_n-men_yes]], alternative='two-sided')
        answer.append(dict(scenario=name, women_count=women_yes,
                           women_rate=women_yes/women_n, men_count=men_yes,
                           men_rate=men_yes/men_n, p=float(p), odds_ratio=float(odds)))
    return answer


def calculations():
    d = number_map('datepsych_2023_reported.csv')
    original = {r['metric']:float(r['value']) for r in rows('den_haese_king_2022_sample.csv')}
    counts_sum = sum(int(d[k]) for k in ['sex_partners_more','oral_partners_more','partner_counts_equal'])
    implied_male = int(d['oral_partners_more']-d['oral_partners_more_women'])
    max_sd = max_sample_sd(12, d['oral_gt_difference_women_min'],d['oral_gt_difference_women_max'])
    implied_mean = (12*d['oral_gt_difference_women_mean'] + implied_male*d['oral_gt_difference_men_mean'])/(12+implied_male)
    female_approx = original['analytic_n'] * original['female_share']/100
    overall_ci = fisher_z_ci(d['sex_partner_sd_r_all'],int(d['total_n']))
    female_ci = fisher_z_ci(d['sex_partner_sd_r_women'],int(d['women_n']))
    return dict(category_total=counts_sum, reported_n=int(d['total_n']),
                category_excess=counts_sum-int(d['total_n']),
                implied_male_oral_greater=implied_male,
                implied_male_rate=implied_male/d['men_n'],
                sd_max=max_sd, sd_reported=d['oral_gt_difference_women_sd'],
                pooled_mean_implied=implied_mean,
                pooled_mean_reported=d['oral_gt_difference_all_mean'],
                female_original_approx=female_approx,
                original_no_yes_women_share=65/female_approx,
                overall_corr_ci=overall_ci,
                female_corr_ci=female_ci,
                scenarios=scenarios())


def report_text(c):
    lines = [
        'Does Oral Sex Count? — Published-summary reconstructions',
        'IMPORTANT: calculations from rounded published statistics, not participant-level replication.',
        '',
        f'Category totals: 140 + 57 + 443 = {c["category_total"]}, versus stated n={c["reported_n"]}; excess={c["category_excess"]}.',
        f'If 57 total oral-greater includes 12 women, implied men={c["implied_male_oral_greater"]} of 447 ({c["implied_male_rate"]*100:.2f}%), versus published 12.7%.',
        '',
        'Hypothetical two-sided Fisher exact tests (women fixed at 12/181; men vary):',
    ]
    for s in c['scenarios']:
        lines.append(f'  {s["scenario"]}: men={s["men_count"]}/447 ({s["men_rate"]*100:.2f}%); women=12/181 (6.63%); Fisher p={s["p"]:.6f}.')
    lines.extend([
        '',
        f'For n=12 and bounded range 1–3: maximum possible sample SD={c["sd_max"]:.6f}; reported SD={c["sd_reported"]:.2f} (impossible under the stated constraints).',
        f'Implied pooled mean using rounded women 2.1 (n=12), men 2.2 (n=45) = {c["pooled_mean_implied"]:.6f}; published pooled mean={c["pooled_mean_reported"]:.2f}.',
        f'Original sample estimated women=1155*74.6% = {c["female_original_approx"]:.2f}; 65/{c["female_original_approx"]:.2f} = {c["original_no_yes_women_share"]*100:.2f}% of all women, NOT of sexually experienced women.',
        '',
        f'Overall r=-0.02, assumed n=628: approximate Fisher-z 95% CI [{c["overall_corr_ci"][0]:.4f}, {c["overall_corr_ci"][1]:.4f}].',
        f'Women r=-0.11, assumed n=181: approximate Fisher-z 95% CI [{c["female_corr_ci"][0]:.4f}, {c["female_corr_ci"][1]:.4f}].',
        '',
        'YouGov table p.1: overall penis-oral yes=45%, no=41%; these conflict with YouGov article prose, and chart uses tables.',
        'Natsal: men=33.1%, women=23.4% excluding oral-only partners.',
        'Gnambs/Kaspar Table 5, sexuality: relative affirmative reporting=1.29; approximate CI=exp([0.11,0.41])=[1.1163,1.5068].',
        '',
        'No original respondent data or missing eligibility counts are recovered here.',
    ])
    return '\n'.join(lines)+'\n'


def base_style():
    plt.rcParams.update({
        'font.family':'DejaVu Sans', 'font.size':10,'axes.labelcolor':INK,
        'text.color':INK,'axes.edgecolor':'#cbd6da','xtick.color':GREY,
        'ytick.color':GREY,'axes.titleweight':'bold','axes.titlesize':13,
        'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white',
        'axes.spines.top':False,'axes.spines.right':False,
    })


def finish(fig,name):
    fig.savefig(ROOT/name,dpi=DPI,bbox_inches='tight',pad_inches=0.30)
    plt.close(fig)


def fig1_original_groups():
    items=rows('den_haese_king_2022.csv')
    labels=['Oral only; answered NO to “had sex”','Oral only; answered YES to “had sex”']
    means=[float(r['marlowe_crowne_mean']) for r in items]
    fig,ax=plt.subplots(figsize=(10.5,4.3))
    bars=ax.barh([0,1],means,color=[TEAL,LIGHT],height=.48)
    ax.set_yticks([0,1],labels=labels);ax.invert_yaxis();ax.set_xlim(0,33)
    ax.set_xticks([0,5,10,15,20,25,30,33]);ax.set_xlabel('Mean Marlowe–Crowne score (full scale: 0–33)')
    ax.set_title('The original study: different labels, different scale scores',pad=18)
    ax.grid(axis='x',alpha=.17);ax.set_axisbelow(True);ax.spines['left'].set_visible(False)
    ax.tick_params(axis='y',length=0)
    for b,r,m in zip(bars,items,means):
        ax.text(m+.50,b.get_y()+b.get_height()/2,f'{m:.2f}  (n={r["n"]})',va='center',color=INK,fontweight='bold')
    fig.subplots_adjust(left=.32,right=.97,bottom=.22,top=.78)
    finish(fig,'figure_1_original_groups.png')


def fig2_scenarios():
    s=scenarios(); labels=[r['scenario'] for r in s]
    fig,ax=plt.subplots(figsize=(11.4,5.1))
    y=np.arange(3);h=.31
    women=np.array([r['women_rate']*100 for r in s]);men=np.array([r['men_rate']*100 for r in s])
    bw=ax.barh(y-h/2,women,h,color=LIGHT,label='Women (12/181 in each scenario)')
    bm=ax.barh(y+h/2,men,h,color=TEAL,label='Men (alternative implied counts)')
    ax.set_yticks(y, labels=labels);ax.invert_yaxis()
    ax.set_xlim(0,17.0);ax.set_xticks(np.arange(0,18,2));ax.set_xlabel('Percent with more oral-sex partners than “had sex” partners')
    ax.set_title('Three incompatible reconstructions — not three observed findings',pad=25)
    ax.grid(axis='x',alpha=.17);ax.set_axisbelow(True);ax.tick_params(axis='y',length=0);ax.spines['left'].set_visible(False)
    for bars,vals in [(bw,women),(bm,men)]:
        for b,val in zip(bars,vals):
            ax.text(val+.2,b.get_y()+b.get_height()/2,f'{val:.1f}%',va='center',fontsize=9,color=INK)
    # Keep p-values out of the bar lengths themselves.
    for yy,ss in enumerate(s):
        ax.text(16.8,yy,f'p={ss["p"]:.3f}',va='center',ha='right',color=GREY,fontsize=9)
    ax.legend(loc='lower center',bbox_to_anchor=(.5,1.00),ncol=2,frameon=False,fontsize=9)
    fig.subplots_adjust(left=.36,right=.96,bottom=.19,top=.75)
    finish(fig,'figure_2_inconsistent_counts.png')


def fig3_correlations():
    d=number_map('datepsych_2023_reported.csv')
    series=[('All respondents: “had sex” partners', d['sex_partner_sd_r_all'], int(d['total_n'])),
            ('Women: “had sex” partners', d['sex_partner_sd_r_women'], int(d['women_n']))]
    fig,ax=plt.subplots(figsize=(11,4.1))
    for i,(name,r,n) in enumerate(series):
        lo,hi=fisher_z_ci(r,n)
        ax.errorbar(r,i,xerr=[[r-lo],[hi-r]],fmt='o',color=INK,ecolor=TEAL,
                    capsize=5,linewidth=2,markersize=7,zorder=3)
        ax.text(.082,i,f'r={r:+.2f}; 95% CI [{lo:+.2f}, {hi:+.2f}]',va='center',fontsize=9)
    ax.axvline(0,color='#c79c68',linestyle='--',linewidth=1.1)
    ax.set_xlim(-.31,.30);ax.set_xticks([-.3,-.2,-.1,0,.1,.2,.3]);ax.set_ylim(-.6,1.6)
    ax.set_yticks([0,1],labels=[f'{a} (n={n})' for a,_,n in series]);ax.invert_yaxis()
    ax.set_xlabel('Pearson correlation with Marlowe–Crowne score')
    ax.set_title('Near-zero associations do not validate the accuracy of survey reports',pad=18)
    ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True);ax.tick_params(axis='y',length=0);ax.spines['left'].set_visible(False)
    fig.subplots_adjust(left=.32,right=.98,bottom=.23,top=.78)
    finish(fig,'figure_3_correlation_intervals.png')


def fig4_meta_analysis():
    data=rows('gnambs_kaspar_2015_table5.csv')
    y=np.arange(len(data))
    point=np.array([float(r['pooled_relative_reporting_ratio']) for r in data])
    lo=np.exp([float(r['log_ci_lower']) for r in data]);hi=np.exp([float(r['log_ci_upper']) for r in data])
    fig,ax=plt.subplots(figsize=(11,5.4))
    ax.errorbar(point,y,xerr=[point-lo,hi-point],fmt='o',color=INK,ecolor=TEAL,
                capsize=4,elinewidth=2,markersize=7)
    for i,r in enumerate(data):
        ax.text(1.73,i,f'{point[i]:.2f}',va='center',ha='right',color=INK,fontsize=10)
    ax.set_yticks(y,labels=[r['category'] for r in data]);ax.invert_yaxis();ax.set_xlim(.88,1.80)
    ax.axvline(1,color='#c79c68',linestyle='--',linewidth=1.1)
    ax.set_xlabel('Relative affirmative reporting (computer / paper); 95% CI')
    ax.set_title('Computerized questionnaires often elicited more sensitive disclosures',pad=19)
    ax.grid(axis='x',alpha=.16);ax.set_axisbelow(True);ax.tick_params(axis='y',length=0);ax.spines['left'].set_visible(False)
    fig.subplots_adjust(left=.22,right=.98,bottom=.18,top=.83)
    finish(fig,'figure_4_survey_mode.png')


def fig5_natsal():
    natsal=rows('natsal_2019.csv')
    lookup={(r['measure'],r['group']):float(r['value']) for r in natsal}
    names=['Men','Women']; vals=[lookup[('oral_only_excluded',name)] for name in names]
    fig,ax=plt.subplots(figsize=(10.5,4.5))
    bars=ax.barh([0,1],vals,color=[TEAL,LIGHT],height=.5)
    ax.set_yticks([0,1],labels=names);ax.invert_yaxis()
    ax.set_xlim(0,45);ax.set_xticks(np.arange(0,46,5));ax.set_xlabel('Excluded oral-only partners from reported partner total (%)')
    ax.set_title('Natsal-3: men excluded oral-only partners more often',pad=20)
    ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True);ax.tick_params(axis='y',length=0);ax.spines['left'].set_visible(False)
    for b,v in zip(bars,vals):ax.text(v+.4,b.get_y()+b.get_height()/2,f'{v:.1f}%',va='center',fontweight='bold')
    fig.subplots_adjust(left=.14,right=.94,bottom=.21,top=.78)
    finish(fig,'figure_5_natsal_oral_only.png')


def fig6_yougov():
    data=[r for r in rows('yougov_2023_page1.csv') if r['behavior']=='Oral stimulation of penis' and r['age_group']!='All adults']
    labels=[r['age_group'] for r in data]
    yes=np.array([float(r['yes_pct']) for r in data]);no=np.array([float(r['no_pct']) for r in data])
    x=np.arange(len(data));w=.37
    fig,ax=plt.subplots(figsize=(10.5,5.2))
    a=ax.bar(x-w/2,yes,width=w,label='Counts as “having sex”',color=TEAL)
    b=ax.bar(x+w/2,no,width=w,label='Does not count',color=LIGHT)
    ax.set_xticks(x,labels=labels);ax.set_ylim(0,70);ax.set_ylabel('Weighted percentage of respondents')
    ax.set_title('YouGov: Does oral stimulation of the penis alone count as “having sex”?',pad=28)
    ax.legend(loc='upper center',bbox_to_anchor=(.5,1.01),ncol=2,frameon=False,fontsize=9)
    ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True);ax.spines['left'].set_visible(False)
    for bars in (a,b):
        for rect in bars:
            ax.text(rect.get_x()+rect.get_width()/2,rect.get_height()+1,f'{rect.get_height():.0f}%',ha='center',va='bottom',fontsize=9)
    fig.text(.5,.025,'“Don’t know” and “prefer not to say” not plotted; all responses preserved in the CSV.',ha='center',fontsize=9,color=GREY)
    fig.subplots_adjust(left=.10,right=.98,bottom=.18,top=.79)
    finish(fig,'figure_6_yougov_age.png')


def main():
    base_style()
    c=calculations()
    out=report_text(c)
    print(out,end='')
    (ROOT/'reconstruction_results.txt').write_text(out,encoding='utf-8')
    for task in [fig1_original_groups,fig2_scenarios,fig3_correlations,
                 fig4_meta_analysis,fig5_natsal,fig6_yougov]:task()
    print('Regenerated six figures and reconstruction_results.txt')

if __name__=='__main__':
    main()
