"""Tests for the published-summary arithmetic; no original-data tests are possible."""
import csv
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from reproduce_oral_sex_figures import calculations, fisher_z_ci, max_sample_sd, rows, scenarios

class TestReconstruction(unittest.TestCase):
    def test_incompatible_category_totals(self):
        c=calculations()
        self.assertEqual(c['category_total'],640)
        self.assertEqual(c['reported_n'],628)
        self.assertEqual(c['category_excess'],12)

    def test_implied_male_rate(self):
        c=calculations()
        self.assertEqual(c['implied_male_oral_greater'],45)
        self.assertAlmostEqual(c['implied_male_rate']*100,10.067114,places=5)

    def test_fisher_sensitivity(self):
        r=scenarios()
        self.assertEqual([x['men_count'] for x in r],[33,45,57])
        for result,target in zip(r,[.865,.220,.025]):
            self.assertAlmostEqual(result['p'],target,delta=.002)

    def test_sd_upper_bound(self):
        c=calculations()
        self.assertAlmostEqual(c['sd_max'], math.sqrt(12/11), places=8)
        self.assertLess(c['sd_max'],c['sd_reported'])

    def test_pooled_mean_sensitivity(self):
        c=calculations()
        self.assertAlmostEqual(c['pooled_mean_implied'],(12*2.1+45*2.2)/57,places=8)
        self.assertGreater(c['pooled_mean_implied']-c['pooled_mean_reported'],0.04)

    def test_original_study_group_numbers(self):
        data=rows('den_haese_king_2022.csv')
        self.assertEqual([int(r['n']) for r in data],[77,30])
        self.assertEqual([int(r['women_n']) for r in data],[65,19])
        self.assertEqual([float(r['marlowe_crowne_mean']) for r in data],[14.99,11.47])
        self.assertEqual([float(r['religiosity_mean']) for r in data],[4.22,3.17])

    def test_original_female_denominator(self):
        c=calculations()
        self.assertAlmostEqual(c['female_original_approx'],861.63,places=2)
        self.assertAlmostEqual(c['original_no_yes_women_share']*100,7.54384,places=4)

    def test_correlation_ci(self):
        c=calculations()
        lo,hi=c['overall_corr_ci'];self.assertAlmostEqual(lo,-.098,delta=.003);self.assertAlmostEqual(hi,.058,delta=.003)
        lo,hi=c['female_corr_ci'];self.assertAlmostEqual(lo,-.252,delta=.004);self.assertAlmostEqual(hi,.036,delta=.004)

    def test_meta_table5_scale(self):
        data={r['category']:r for r in rows('gnambs_kaspar_2015_table5.csv')}
        sex=data['Sexuality']
        self.assertEqual(int(sex['effects']),51)
        self.assertEqual(int(sex['samples']),20)
        self.assertEqual(int(sex['reported_subgroup_n']),17966)
        self.assertAlmostEqual(float(sex['pooled_relative_reporting_ratio']),1.29)
        self.assertAlmostEqual(math.exp(float(sex['log_ci_lower'])),1.116278,places=5)
        self.assertAlmostEqual(math.exp(float(sex['log_ci_upper'])),1.506817,places=5)

    def test_natsal(self):
        d={(r['measure'],r['group']):float(r['value']) for r in rows('natsal_2019.csv')}
        self.assertEqual((d['oral_only_excluded','Men'],d['oral_only_excluded','Women']),(33.1,23.4))
        self.assertEqual((d['past_year_gap','Before adding omitted oral-only partners'],
                          d['past_year_gap','After adding omitted oral-only partners']),(0.23,0.28))

    def test_yougov_age_rows_and_overall(self):
        d={(r['behavior'],r['age_group']):r for r in rows('yougov_2023_page1.csv')}
        self.assertEqual((int(d['Oral stimulation of penis','All adults']['yes_pct']),
                          int(d['Oral stimulation of penis','All adults']['no_pct'])),(45,41))
        expected={'18–24':(28,52),'25–49':(36,51),'50–64':(56,30),'65+':(56,28)}
        for age,pair in expected.items():
            row=d['Oral stimulation of penis',age]
            self.assertEqual((int(row['yes_pct']),int(row['no_pct'])),pair)

    def test_expected_figure_names(self):
        for name in ['figure_1_original_groups.png','figure_2_inconsistent_counts.png',
                     'figure_3_correlation_intervals.png','figure_4_survey_mode.png',
                     'figure_5_natsal_oral_only.png','figure_6_yougov_age.png']:
            self.assertTrue((ROOT/name).is_file(),name)
            self.assertGreater((ROOT/name).stat().st_size,5000,name)

if __name__=='__main__':unittest.main()
