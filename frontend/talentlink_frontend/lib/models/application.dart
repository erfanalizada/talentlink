class Application {
  final String id;
  final String jobId;
  final String employeeId;
  final String? cvId;
  final String status;
  final double? matchScore;
  final String? matchSummary;
  final DateTime appliedAt;
  final Map<String, dynamic>? matchDetails;

  Application({
    required this.id,
    required this.jobId,
    required this.employeeId,
    this.cvId,
    required this.status,
    this.matchScore,
    this.matchSummary,
    required this.appliedAt,
    this.matchDetails,
  });

  factory Application.fromJson(Map<String, dynamic> json) {
    return Application(
      id: json['id'] ?? '',
      jobId: json['job_id'] ?? '',
      employeeId: json['employee_id'] ?? '',
      cvId: json['cv_id'],
      status: json['status'] ?? 'pending',
      matchScore: json['match_score']?.toDouble(),
      matchSummary: json['match_summary'],
      appliedAt: DateTime.parse(json['applied_at'] ?? DateTime.now().toIso8601String()),
      matchDetails: json['match_details'],
    );
  }

  String getStatusDisplay() {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'Pending Review';
      case 'reviewed':
        return 'Reviewed';
      case 'invited':
        return 'Interview Invited';
      case 'rejected':
        return 'Not Selected';
      default:
        return status;
    }
  }

  String getMatchScoreDisplay() {
    if (matchScore == null) return 'Calculating...';
    return '${matchScore!.toStringAsFixed(0)}%';
  }
}
