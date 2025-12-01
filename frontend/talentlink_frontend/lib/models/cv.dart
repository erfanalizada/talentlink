class CV {
  final String id;
  final String userId;
  final String fileName;
  final int fileSize;
  final String contentType;
  final DateTime uploadedAt;

  CV({
    required this.id,
    required this.userId,
    required this.fileName,
    required this.fileSize,
    required this.contentType,
    required this.uploadedAt,
  });

  factory CV.fromJson(Map<String, dynamic> json) {
    return CV(
      id: json['id'] ?? '',
      userId: json['user_id'] ?? '',
      fileName: json['file_name'] ?? '',
      fileSize: json['file_size'] ?? 0,
      contentType: json['content_type'] ?? '',
      uploadedAt: DateTime.parse(json['uploaded_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  String getFileSizeDisplay() {
    if (fileSize < 1024) return '$fileSize B';
    if (fileSize < 1024 * 1024) return '${(fileSize / 1024).toStringAsFixed(1)} KB';
    return '${(fileSize / (1024 * 1024)).toStringAsFixed(1)} MB';
  }
}
