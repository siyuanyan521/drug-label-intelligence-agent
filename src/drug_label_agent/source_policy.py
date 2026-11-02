"""Offline decisions from recorded evidence; no network or publication side effects."""
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlsplit, unquote


class FileStatus(str, Enum):
    DOWNLOADED = 'DOWNLOADED'
    DOWNLOAD_FAILED = 'DOWNLOAD_FAILED'
    INVALID_FILE = 'INVALID_FILE'


class ContentStatus(str, Enum):
    VERIFIED = 'VERIFIED'
    NEEDS_REVIEW = 'NEEDS_REVIEW'
    REJECTED = 'REJECTED'


class SourceStatus(str, Enum):
    OFFICIAL = 'OFFICIAL'
    VERIFIED_INSTITUTION = 'VERIFIED_INSTITUTION'
    THIRD_PARTY = 'THIRD_PARTY'
    UNKNOWN = 'UNKNOWN'


class AccessStatus(str, Enum):
    FREE = 'FREE'
    RESTRICTED = 'RESTRICTED'
    UNKNOWN = 'UNKNOWN'


class RedistributionStatus(str, Enum):
    PERMITTED = 'PERMITTED'
    RESTRICTED = 'RESTRICTED'
    UNKNOWN = 'UNKNOWN'


@dataclass(frozen=True)
class Product:
    # Canonical, evidence-backed identifiers, not substring/fuzzy matches.
    ingredient: str
    formulation: str
    salt: str
    route: str
    combination: tuple[str, ...] = ()


def product_match(target: Product, candidate: Product) -> bool:
    """Missing identity fields cannot establish equivalence."""
    return all((target.ingredient, target.formulation, target.salt, target.route)) and target == candidate


@dataclass(frozen=True)
class Candidate:
    url: str
    file_status: FileStatus | None = None  # None: not attempted; never fabricate failure.
    content_status: ContentStatus = ContentStatus.NEEDS_REVIEW
    source_status: SourceStatus = SourceStatus.UNKNOWN
    access_status: AccessStatus = AccessStatus.UNKNOWN
    redistribution_status: RedistributionStatus = RedistributionStatus.UNKNOWN
    language: str = 'unknown'  # zh: reviewed Chinese body; English brand names are allowed.
    complete_formal_label: bool = False
    product_identity_verified: bool = False
    source_evidence: tuple[str, ...] = ()
    access_terms_confirmed: bool = False
    download_use_allowed: bool = False
    redistribution_evidence: tuple[str, ...] = ()
    upstream_urls: tuple[str, ...] = ()  # Known origins, including excluded mirrors.
    trace: dict = field(default_factory=dict)


@dataclass(frozen=True)
class AdoptionPolicy:
    accepted_sources: frozenset[SourceStatus] = frozenset({
        SourceStatus.OFFICIAL, SourceStatus.VERIFIED_INSTITUTION})
    excluded_domains: tuple[str, ...] = ('dxy.cn', 'dxy.com')


@dataclass(frozen=True)
class Decision:
    retain_candidate: bool
    may_download: bool
    final_qualified: bool
    manual_review: bool
    may_publish: bool
    reasons: tuple[str, ...]


def discovery_queries(name: str, brand: str = '', holder: str = '', approval: str = '') -> list[str]:
    pairs = [(name, '说明书 PDF'), (brand, '说明书下载'),
             (f'{name} {holder}' if holder else '', 'PDF'),
             (f'{brand} {approval}' if brand and approval else '', '说明书'),
             (name, '中文说明书')]
    return list(dict.fromkeys(f'{value.strip()} {suffix}' for value, suffix in pairs if value.strip()))


def trace_queries(url: str, title: str = '', approval: str = '') -> list[str]:
    """Plan provenance searches from observed evidence, never invent file paths."""
    filename = unquote(urlsplit(url).path.rsplit('/', 1)[-1])
    return list(dict.fromkeys(x for x in (url, filename, title.strip(), approval.strip()) if x))


def evaluate(c: Candidate, policy: AdoptionPolicy = AdoptionPolicy()) -> Decision:
    for key, enum in [('file_status', FileStatus), ('content_status', ContentStatus),
                      ('source_status', SourceStatus), ('access_status', AccessStatus),
                      ('redistribution_status', RedistributionStatus)]:
        value = getattr(c, key)
        if not (key == 'file_status' and value is None):
            enum(value)  # Fail loudly for misspelled states.
    hosts = [(urlsplit(url).hostname or '').lower() for url in (c.url, *c.upstream_urls)]
    excluded = any(host == d or host.endswith('.' + d)
                   for host in hosts for d in policy.excluded_domains)
    if excluded or c.access_status == AccessStatus.RESTRICTED:
        return Decision(False, False, False, False, False,
                        ('PROJECT_EXCLUDED_SOURCE' if excluded else 'RESTRICTED_ACCESS',))
    if c.language not in ('zh', 'unknown'):
        return Decision(False, False, False, False, False, ('NON_CHINESE_BODY',))
    if c.file_status == FileStatus.INVALID_FILE or c.content_status == ContentStatus.REJECTED:
        return Decision(False, False, False, False, False, ('INVALID_OR_REJECTED_CONTENT',))
    reasons = []
    may_download = (c.access_status == AccessStatus.FREE and c.access_terms_confirmed
                    and c.download_use_allowed)
    if not may_download:
        reasons.append('ACCESS_OR_USE_TERMS_UNCONFIRMED')
    content_ok = (c.language == 'zh' and c.content_status == ContentStatus.VERIFIED
                  and c.complete_formal_label and c.product_identity_verified)
    if not content_ok:
        reasons.append('CONTENT_OR_PRODUCT_REVIEW_REQUIRED')
    source_ok = c.source_status in policy.accepted_sources
    # Explicit third-party admission still needs documented evidence, never FREE alone.
    if not source_ok or not c.source_evidence or c.source_status == SourceStatus.UNKNOWN:
        source_ok = False
        reasons.append('SOURCE_TRACE_REQUIRED')
    qualified = (may_download and content_ok and source_ok
                 and c.file_status == FileStatus.DOWNLOADED)
    publish = (qualified and c.redistribution_status == RedistributionStatus.PERMITTED
               and bool(c.redistribution_evidence))
    # This is eligibility only. No API in this module uploads or pushes anything.
    return Decision(True, may_download, qualified, not qualified, publish, tuple(reasons))
