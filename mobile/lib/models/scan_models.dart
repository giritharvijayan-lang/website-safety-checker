class Signal {
  final String name;
  final String description;
  final String severity;
  final Map<String, dynamic>? details;

  Signal({
    required this.name,
    required this.description,
    this.severity = 'INFO',
    this.details,
  });

  factory Signal.fromJson(Map<String, dynamic> json) {
    return Signal(
      name: json['name'] as String? ?? 'Signal',
      description: json['description'] as String? ?? '',
      severity: json['severity'] as String? ?? 'INFO',
      details: json['details'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'name': name,
        'description': description,
        'severity': severity,
        'details': details,
      };
}

class CategoryResult {
  final String name;
  final int score;
  final String riskLevel;
  final List<Signal> signals;
  final Map<String, dynamic>? details;

  CategoryResult({
    required this.name,
    required this.score,
    required this.riskLevel,
    required this.signals,
    this.details,
  });

  factory CategoryResult.fromJson(Map<String, dynamic> json) {
    return CategoryResult(
      name: json['name'] as String? ?? '',
      score: (json['score'] as num?)?.toInt() ?? 0,
      riskLevel: json['risk_level'] as String? ?? 'UNKNOWN',
      signals: (json['signals'] as List<dynamic>?)
              ?.map((e) => Signal.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      details: json['details'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'name': name,
        'score': score,
        'risk_level': riskLevel,
        'signals': signals.map((e) => e.toJson()).toList(),
        'details': details,
      };

  String get displayName {
    switch (name) {
      case 'phishing':
        return 'Phishing & Impersonation';
      case 'malware':
        return 'Malware & Threat Intel';
      case 'shopping_trust':
        return 'Shopping & E-Commerce Trust';
      case 'scam_offer':
        return 'Scam Offers & Artificial Urgency';
      case 'connection_security':
        return 'Connection Security & SSL';
      case 'trackers':
        return 'Trackers & Privacy';
      case 'reputation':
        return 'Domain Reputation & Age';
      default:
        return name.replaceAll('_', ' ').toUpperCase();
    }
  }
}

class OverallResult {
  final int score;
  final String verdict;
  final String label;
  final String? summary;
  final String? maxRiskCategory;

  OverallResult({
    required this.score,
    required this.verdict,
    required this.label,
    this.summary,
    this.maxRiskCategory,
  });

  factory OverallResult.fromJson(Map<String, dynamic> json) {
    return OverallResult(
      score: (json['score'] as num?)?.toInt() ?? 0,
      verdict: json['verdict'] as String? ?? 'UNKNOWN',
      label: json['label'] as String? ?? '',
      summary: json['summary'] as String?,
      maxRiskCategory: json['max_risk_category'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'score': score,
        'verdict': verdict,
        'label': label,
        'summary': summary,
        'max_risk_category': maxRiskCategory,
      };
}

class ScanResponse {
  final String scanId;
  final String url;
  final String domain;
  final String siteType;
  final OverallResult overall;
  final List<CategoryResult> categories;

  ScanResponse({
    required this.scanId,
    required this.url,
    required this.domain,
    required this.siteType,
    required this.overall,
    required this.categories,
  });

  factory ScanResponse.fromJson(Map<String, dynamic> json) {
    return ScanResponse(
      scanId: json['scan_id'] as String? ?? '',
      url: json['url'] as String? ?? '',
      domain: json['domain'] as String? ?? '',
      siteType: json['site_type'] as String? ?? 'general',
      overall: OverallResult.fromJson(json['overall'] as Map<String, dynamic>),
      categories: (json['categories'] as List<dynamic>?)
              ?.map((e) => CategoryResult.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() => {
        'scan_id': scanId,
        'url': url,
        'domain': domain,
        'site_type': siteType,
        'overall': overall.toJson(),
        'categories': categories.map((e) => e.toJson()).toList(),
      };
}
