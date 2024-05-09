from django.db import models

class Post(models.Model):
    body = models.TextField()

class AnalysisDocument(models.Model):
    post = models.ForeignKey(Post, related_name='analysis_docs', on_delete=models.CASCADE)
    llm = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    analysis = models.TextField()
    category = models.CharField(max_length=100)
    reference_id = models.CharField(max_length=100)
    schema_version = models.CharField(max_length=100)

class MarkdownContent(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()

    class Meta:
        verbose_name_plural = "Markdown content"

    def __str__(self):
        return self.title
