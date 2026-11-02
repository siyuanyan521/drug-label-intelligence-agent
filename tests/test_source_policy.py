import sys
import unittest
from pathlib import Path
from dataclasses import replace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from drug_label_agent.source_policy import (
    Candidate, AdoptionPolicy, Product, FileStatus, ContentStatus, SourceStatus,
    AccessStatus, RedistributionStatus, evaluate, discovery_queries, trace_queries, product_match)


class SourcePolicyTests(unittest.TestCase):
    def candidate(self, **kwargs):
        return replace(Candidate('https://cdn.example.org/public/label.pdf'), **kwargs)

    def verified(self, **kwargs):
        c = self.candidate(file_status=FileStatus.DOWNLOADED, language='zh',
            content_status=ContentStatus.VERIFIED, complete_formal_label=True,
            product_identity_verified=True, access_status=AccessStatus.FREE,
            access_terms_confirmed=True, download_use_allowed=True)
        return replace(c, **kwargs)

    def test_unknown_cdn_retained_at_discovery(self):
        d = evaluate(self.candidate())
        self.assertTrue(d.retain_candidate)
        self.assertTrue(d.manual_review)
        self.assertFalse(d.may_download)

    def test_download_can_succeed_while_source_unknown(self):
        c = self.verified()
        self.assertEqual(c.file_status, FileStatus.DOWNLOADED)
        self.assertEqual(c.source_status, SourceStatus.UNKNOWN)
        self.assertTrue(evaluate(c).may_download)
        self.assertFalse(evaluate(c).final_qualified)
        self.assertTrue(evaluate(c).manual_review)

    def test_unknown_never_official_or_publishable(self):
        c = self.verified(redistribution_status=RedistributionStatus.PERMITTED,
                          redistribution_evidence=('observed license',))
        self.assertEqual(c.source_status, SourceStatus.UNKNOWN)
        self.assertFalse(evaluate(c).may_publish)

    def test_chinese_and_english_handled_differently(self):
        self.assertTrue(evaluate(self.verified()).retain_candidate)
        for language in ['en', 'ja']:
            self.assertFalse(evaluate(self.verified(language=language)).retain_candidate)

    def test_formulation_salt_route_and_combination_are_not_merged(self):
        a = Product('paclitaxel', 'albumin-bound injection', 'none', 'IV')
        self.assertTrue(product_match(a, a))
        for b in [replace(a, formulation='ordinary injection'), replace(a, salt='other'),
                  replace(a, route='oral'), replace(a, combination=('other ingredient',))]:
            self.assertFalse(product_match(a, b))
        self.assertFalse(product_match(replace(a, formulation=''), replace(a, formulation='')))

    def test_paid_source_excluded(self):
        d = evaluate(self.verified(access_status=AccessStatus.RESTRICTED))
        self.assertFalse(d.retain_candidate or d.may_download or d.final_qualified or d.may_publish)

    def test_free_is_not_use_or_redistribution_permission(self):
        c = self.verified(source_status=SourceStatus.OFFICIAL, source_evidence=('official product page',))
        self.assertTrue(evaluate(c).final_qualified)
        self.assertFalse(evaluate(c).may_publish)
        self.assertFalse(evaluate(replace(c, download_use_allowed=False)).may_download)

    def test_official_claim_without_evidence_not_adopted(self):
        self.assertFalse(evaluate(self.verified(source_status=SourceStatus.OFFICIAL)).final_qualified)

    def test_verified_source_and_license_eligible_but_no_upload(self):
        c = self.verified(source_status=SourceStatus.OFFICIAL, source_evidence=('official-page-link',),
            redistribution_status=RedistributionStatus.PERMITTED,
            redistribution_evidence=('publisher permission URL',))
        self.assertTrue(evaluate(c).may_publish)
        self.assertFalse(evaluate(replace(c, file_status=FileStatus.DOWNLOAD_FAILED)).final_qualified)

    def test_third_party_requires_explicit_adoption_policy(self):
        c = self.verified(source_status=SourceStatus.THIRD_PARTY, source_evidence=('reviewed attribution',))
        self.assertFalse(evaluate(c).final_qualified)
        p = AdoptionPolicy(accepted_sources=frozenset({SourceStatus.THIRD_PARTY}))
        self.assertTrue(evaluate(c, p).final_qualified)
        self.assertFalse(evaluate(replace(c, source_status=SourceStatus.UNKNOWN), p).final_qualified)

    def test_excluded_database_and_mirror_evidence(self):
        self.assertFalse(evaluate(replace(self.verified(), url='https://drugs.dxy.cn/a')).retain_candidate)
        self.assertFalse(evaluate(self.verified(upstream_urls=('https://drugs.dxy.cn/a',))).may_download)
        # A new host cannot make evidence for an excluded source eligible.
        p = AdoptionPolicy(excluded_domains=('mirror.example.org', 'dxy.cn'))
        self.assertFalse(evaluate(Candidate('https://mirror.example.org/a'), p).may_download)

    def test_invalid_file_and_content_rejected(self):
        self.assertFalse(evaluate(self.verified(file_status=FileStatus.INVALID_FILE)).retain_candidate)
        self.assertFalse(evaluate(self.verified(content_status=ContentStatus.REJECTED)).retain_candidate)

    def test_queries_broaden_without_domain_allowlist(self):
        q = discovery_queries('Synthetic drug', 'Demo', 'Holder', 'H00000000')
        self.assertEqual(len(q), 5)
        self.assertFalse(any('site:' in s for s in q))
        self.assertEqual(trace_queries('https://cdn.example.org/a%20label.pdf', 'Label', 'H00000000'),
                         ['https://cdn.example.org/a%20label.pdf', 'a label.pdf', 'Label', 'H00000000'])

    def test_unknown_language_remains_for_review(self):
        self.assertTrue(evaluate(self.verified(language='unknown')).manual_review)
        self.assertFalse(evaluate(self.verified(language='unknown')).final_qualified)

    def test_misspelled_state_raises(self):
        with self.assertRaises(ValueError):
            evaluate(self.candidate(source_status='OFFICAL'))
