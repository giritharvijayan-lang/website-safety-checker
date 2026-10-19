import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/scan_models.dart';
import '../widgets/glass_container.dart';

class ResultScreen extends StatelessWidget {
  final ScanResponse scan;

  const ResultScreen({super.key, required this.scan});

  Future<void> _openInExternalBrowser(BuildContext context) async {
    String urlStr = scan.url.trim();
    if (!urlStr.startsWith('http://') && !urlStr.startsWith('https://')) {
      urlStr = 'https://$urlStr';
    }
    final uri = Uri.tryParse(urlStr);
    if (uri == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Invalid URL format')),
      );
      return;
    }

    if (scan.overall.verdict == 'DANGEROUS' || scan.overall.verdict == 'SUSPICIOUS') {
      final isDangerous = scan.overall.verdict == 'DANGEROUS';
      final bool? proceed = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          backgroundColor: const Color(0xFF19191D),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
            side: BorderSide(
              color: isDangerous ? const Color(0xFFEF4444) : const Color(0xFFF59E0B),
              width: 1.5,
            ),
          ),
          title: Row(
            children: [
              Icon(
                isDangerous ? Icons.gpp_bad_rounded : Icons.warning_amber_rounded,
                color: isDangerous ? const Color(0xFFEF4444) : const Color(0xFFF59E0B),
                size: 26,
              ),
              const SizedBox(width: 10),
              Text(
                isDangerous ? 'Security Alert!' : 'Caution Advised',
                style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                isDangerous
                    ? 'This website has been flagged as DANGEROUS (${scan.overall.maxRiskCategory ?? "high threat"}). Visiting it may expose you to phishing, credential theft, or malicious downloads.'
                    : 'This website has SUSPICIOUS signals (${scan.overall.maxRiskCategory ?? "potential risk"}). Exercise caution before sharing sensitive information.',
                style: const TextStyle(color: Colors.white70, fontSize: 13, height: 1.4),
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.05),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  scan.url,
                  style: const TextStyle(color: Colors.white60, fontSize: 11, fontFamily: 'monospace'),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('Stay Safe (Cancel)', style: TextStyle(color: Colors.white70)),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: isDangerous ? const Color(0xFFEF4444) : const Color(0xFFF59E0B),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('Proceed Anyway', style: TextStyle(fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      );

      if (proceed != true) return;
    }

    try {
      final launched = await launchUrl(uri, mode: LaunchMode.externalApplication);
      if (!launched && context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Could not open external browser for this URL')),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error launching browser: $e')),
        );
      }
    }
  }

  Color _getVerdictColor(String verdict) {
    switch (verdict) {
      case 'DANGEROUS':
        return const Color(0xFFEF4444);
      case 'SUSPICIOUS':
        return const Color(0xFFF59E0B);
      case 'NOT_ENOUGH_INFO':
        return const Color(0xFF64748B);
      case 'LOOKS_OK':
      default:
        return const Color(0xFF10B981);
    }
  }

  IconData _getVerdictIcon(String verdict) {
    switch (verdict) {
      case 'DANGEROUS':
        return Icons.gpp_bad_rounded;
      case 'SUSPICIOUS':
        return Icons.warning_amber_rounded;
      case 'NOT_ENOUGH_INFO':
        return Icons.help_outline_rounded;
      case 'LOOKS_OK':
      default:
        return Icons.verified_user_rounded;
    }
  }

  Color _getSeverityColor(String severity) {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
        return Colors.redAccent.shade400;
      case 'HIGH':
        return Colors.deepOrangeAccent;
      case 'MEDIUM':
        return Colors.amberAccent.shade400;
      case 'LOW':
        return Colors.lightBlueAccent;
      case 'UNKNOWN':
        return Colors.purpleAccent;
      case 'INFO':
      default:
        return Colors.blueGrey.shade300;
    }
  }

  void _showWhyThisScoreSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => GlassContainer(
        opacity: 0.16,
        blur: 24,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Row(
                  children: [
                    Icon(Icons.insights, color: Colors.cyanAccent),
                    SizedBox(width: 8),
                    Text(
                      'Why this score?',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                  ],
                ),
                IconButton(
                  icon: const Icon(Icons.close, color: Colors.grey),
                  onPressed: () => Navigator.pop(ctx),
                ),
              ],
            ),
            const Divider(color: Colors.white12),
            const SizedBox(height: 12),
            const Text(
              'Worst-Category-Wins Scoring Engine',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Colors.white),
            ),
            const SizedBox(height: 6),
            const Text(
              'Instead of an average that lets clean categories hide dangers, the score is strictly driven by min(category_scores) minus secondary penalties.',
              style: TextStyle(fontSize: 13, color: Colors.white70),
            ),
            const SizedBox(height: 16),
            GlassContainer(
              opacity: 0.08,
              borderRadius: BorderRadius.circular(14),
              padding: const EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('• Overall Score: ${scan.overall.score} / 100',
                      style: const TextStyle(fontWeight: FontWeight.w600, color: Colors.white, fontSize: 13)),
                  const SizedBox(height: 4),
                  Text('• Top Verdict: ${scan.overall.label}',
                      style: const TextStyle(fontWeight: FontWeight.w600, color: Color(0xFFFD366E), fontSize: 13)),
                  if (scan.overall.maxRiskCategory != null) ...[
                    const SizedBox(height: 4),
                    Text('• Driving Factor: ${scan.overall.maxRiskCategory}',
                        style: const TextStyle(fontWeight: FontWeight.w600, color: Colors.white70, fontSize: 13)),
                  ],
                  if (scan.overall.summary != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 8.0),
                      child: Text(scan.overall.summary!,
                          style: const TextStyle(fontSize: 12, color: Colors.white60)),
                    ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'Anti-False-Positive Guardrails',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.white),
            ),
            const SizedBox(height: 6),
            const Text(
              '• Soft categories require at least 2 independent signals before reaching HIGH risk.\n• New domains (<90 days) with no scam signals return NOT_ENOUGH_INFO rather than false high risk.',
              style: TextStyle(fontSize: 12, color: Colors.white70),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final verdictColor = _getVerdictColor(scan.overall.verdict);
    final verdictIcon = _getVerdictIcon(scan.overall.verdict);

    return Scaffold(
      backgroundColor: const Color(0xFF141416),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Text(scan.domain, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
        actions: [
          IconButton(
            icon: const Icon(Icons.open_in_new_rounded, color: Colors.white70),
            tooltip: 'Open in External Browser',
            onPressed: () => _openInExternalBrowser(context),
          ),
          IconButton(
            icon: const Icon(Icons.help_outline, color: Color(0xFFFD366E)),
            tooltip: 'Why this score?',
            onPressed: () => _showWhyThisScoreSheet(context),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Glass Verdict Banner
            GlassContainer(
              opacity: 0.12,
              borderRadius: BorderRadius.circular(24),
              border: Border.all(color: verdictColor.withOpacity(0.4), width: 1.5),
              padding: const EdgeInsets.all(22),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          Icon(verdictIcon, color: verdictColor, size: 28),
                          const SizedBox(width: 10),
                          Text(
                            scan.overall.verdict,
                            style: TextStyle(
                              color: verdictColor,
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              letterSpacing: 0.5,
                            ),
                          ),
                        ],
                      ),
                      GlassContainer(
                        opacity: 0.15,
                        borderRadius: BorderRadius.circular(20),
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                        child: Text(
                          '${scan.overall.score} / 100',
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    scan.overall.label,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    scan.url,
                    style: const TextStyle(
                      color: Colors.white54,
                      fontSize: 12,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),

            // Prominent "Open in External Browser" Action Button
            ElevatedButton(
              onPressed: () => _openInExternalBrowser(context),
              style: ElevatedButton.styleFrom(
                backgroundColor: scan.overall.verdict == 'LOOKS_OK'
                    ? const Color(0xFF10B981)
                    : (scan.overall.verdict == 'DANGEROUS'
                        ? const Color(0xFFEF4444)
                        : (scan.overall.verdict == 'SUSPICIOUS'
                            ? const Color(0xFFF59E0B)
                            : const Color(0xFFFD366E))),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                elevation: 4,
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    scan.overall.verdict == 'LOOKS_OK'
                        ? Icons.open_in_new_rounded
                        : (scan.overall.verdict == 'DANGEROUS'
                            ? Icons.gpp_bad_outlined
                            : Icons.warning_amber_rounded),
                    size: 20,
                  ),
                  const SizedBox(width: 10),
                  Text(
                    scan.overall.verdict == 'LOOKS_OK'
                        ? 'Open in External Browser'
                        : (scan.overall.verdict == 'DANGEROUS'
                            ? 'Open in Browser (Dangerous Warning)'
                            : 'Open in Browser (Proceed with Caution)'),
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),

            // Glass "Why this score?" trigger pill
            InkWell(
              onTap: () => _showWhyThisScoreSheet(context),
              borderRadius: BorderRadius.circular(16),
              child: GlassContainer(
                opacity: 0.06,
                borderRadius: BorderRadius.circular(16),
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                child: const Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.info_outline_rounded, color: Color(0xFFFD366E), size: 18),
                        SizedBox(width: 8),
                        Text(
                          'How was this score calculated?',
                          style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13, color: Colors.white),
                        ),
                      ],
                    ),
                    Icon(Icons.arrow_forward_ios_rounded, size: 13, color: Colors.white38),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 22),

            // Category Breakdown Section Header
            const Text(
              'Security Breakdown (7 Categories)',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
            ),
            const SizedBox(height: 12),

            // Expandable Glass Category Cards
            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: scan.categories.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                final cat = scan.categories[index];
                return _buildGlassCategoryCard(context, cat);
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGlassCategoryCard(BuildContext context, CategoryResult cat) {
    Color riskColor;
    switch (cat.riskLevel) {
      case 'CRITICAL':
        riskColor = Colors.redAccent.shade400;
        break;
      case 'HIGH':
        riskColor = Colors.deepOrangeAccent;
        break;
      case 'MEDIUM':
        riskColor = Colors.amberAccent.shade400;
        break;
      case 'LOW':
        riskColor = Colors.lightBlueAccent;
        break;
      case 'NOT_ENOUGH_INFO':
        riskColor = Colors.blueGrey;
        break;
      case 'UNKNOWN':
        riskColor = Colors.purpleAccent;
        break;
      case 'SAFE':
      default:
        riskColor = const Color(0xFF10B981);
        break;
    }

    return GlassContainer(
      opacity: 0.05,
      borderRadius: BorderRadius.circular(18),
      border: Border.all(color: Colors.white.withOpacity(0.09)),
      child: Theme(
        data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
        child: ExpansionTile(
          tilePadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
          leading: Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: riskColor.withOpacity(0.15),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: riskColor.withOpacity(0.3)),
            ),
            alignment: Alignment.center,
            child: Text(
              '${cat.score}',
              style: TextStyle(color: riskColor, fontWeight: FontWeight.bold, fontSize: 13),
            ),
          ),
          title: Text(
            cat.displayName,
            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.white),
          ),
          subtitle: Text(
            'Risk: ${cat.riskLevel} (${cat.signals.length} signal${cat.signals.length == 1 ? '' : 's'})',
            style: TextStyle(color: riskColor, fontSize: 11),
          ),
          childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
          children: [
            if (cat.signals.isEmpty)
              Container(
                padding: const EdgeInsets.symmetric(vertical: 8),
                alignment: Alignment.centerLeft,
                child: const Text(
                  'No threats or risk signals detected in this category.',
                  style: TextStyle(color: Colors.white38, fontSize: 12),
                ),
              )
            else
              ...cat.signals.map(
                (s) => Container(
                  margin: const EdgeInsets.only(top: 8),
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.03),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: _getSeverityColor(s.severity).withOpacity(0.25)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            s.name.replaceAll('_', ' ').toUpperCase(),
                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 11, color: Colors.white),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: _getSeverityColor(s.severity).withOpacity(0.2),
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: _getSeverityColor(s.severity).withOpacity(0.4)),
                            ),
                            child: Text(
                              s.severity,
                              style: TextStyle(color: _getSeverityColor(s.severity), fontSize: 9, fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      Text(s.description, style: const TextStyle(fontSize: 12, color: Colors.white70)),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
