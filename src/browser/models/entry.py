"""Define the Entry model."""
from django.db import models


class Entry(models.Model):
    """Represents a dictionary entry."""

    id = models.AutoField(verbose_name="id", primary_key=True)
    title_word = models.TextField(max_length=100,
                                  null=False,
                                  blank=False,
                                  db_index=True)
    title_word_md5 = models.TextField(max_length=32,
                                      null=False,
                                      blank=False,
                                      db_index=True)
    title_word_normalized = models.TextField(max_length=100,
                                             null=False,
                                             blank=False,
                                             db_index=True)
    title_word_normalized_md5 = models.TextField(max_length=32,
                                                 null=False,
                                                 blank=False,
                                                 db_index=True)
    text_html = models.TextField(max_length=250_000, null=False)
    text_md5 = models.TextField(max_length=32,
                                null=False,
                                blank=False,
                                db_index=True)
    version = models.PositiveSmallIntegerField(null=False,
                                               blank=False,
                                               default=1,
                                               editable=False)
    row_creation_timestamp = models.DateTimeField(auto_now_add=True)
    row_update_timestamp = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Save the entry to the database."""
        if not self.id:
            self.version = 1
        else:
            self.version = self.version + 1

        return super(Entry, self).save(*args, **kwargs)

    def __str__(self):
        """Override the string representation of the model."""
        return self.title_word
