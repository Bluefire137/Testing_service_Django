# Generated by Django 5.0.7 on 2024-08-08 16:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_testing_service', '0002_remove_useranswer_selected_answers_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='useranswer',
            name='test',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app_testing_service.test'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usertestresult',
            name='total_correct_questions',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
