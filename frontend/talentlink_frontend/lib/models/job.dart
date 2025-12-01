class Job {
  final String id;
  final String employerId;
  final String title;
  final String description;
  final String companyName;
  final List<String> requiredSkills;
  final List<String> requiredTechnologies;
  final int experienceYears;
  final String location;
  final String employmentType;
  final String status;
  final DateTime createdAt;

  Job({
    required this.id,
    required this.employerId,
    required this.title,
    required this.description,
    required this.companyName,
    required this.requiredSkills,
    required this.requiredTechnologies,
    required this.experienceYears,
    required this.location,
    required this.employmentType,
    required this.status,
    required this.createdAt,
  });

  factory Job.fromJson(Map<String, dynamic> json) {
    return Job(
      id: json['id'] ?? '',
      employerId: json['employer_id'] ?? '',
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      companyName: json['company_name'] ?? '',
      requiredSkills: List<String>.from(json['required_skills'] ?? []),
      requiredTechnologies: List<String>.from(json['required_technologies'] ?? []),
      experienceYears: json['experience_years'] ?? 0,
      location: json['location'] ?? '',
      employmentType: json['employment_type'] ?? 'full-time',
      status: json['status'] ?? 'active',
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      'description': description,
      'company_name': companyName,
      'required_skills': requiredSkills,
      'required_technologies': requiredTechnologies,
      'experience_years': experienceYears,
      'location': location,
      'employment_type': employmentType,
    };
  }
}
