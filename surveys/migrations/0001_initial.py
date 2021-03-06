# Generated by Django 4.0 on 2022-01-24 06:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('stucon', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NominationQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=140)),
                ('positive', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='PerceptionQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=140)),
            ],
        ),
        migrations.CreateModel(
            name='SurveyQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=140)),
            ],
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=140)),
                ('peer_feedback', models.BooleanField(default=True)),
                ('topbot5', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
                ('scope', models.CharField(choices=[('cohort', 'Cohort'), ('team', 'Team')], default='team', max_length=10)),
                ('nomination_qs', models.ManyToManyField(to='surveys.NominationQuestion')),
                ('perception_qs', models.ManyToManyField(to='surveys.PerceptionQuestion')),
                ('survey_qs', models.ManyToManyField(to='surveys.SurveyQuestion')),
            ],
        ),
        migrations.CreateModel(
            name='TopFiveResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_as_of', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='top5_author', to='stucon.student')),
                ('survey', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='surveys.survey')),
                ('top_five_select', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stucon.student')),
            ],
            options={
                'unique_together': {('author', 'top_five_select', 'survey')},
            },
        ),
        migrations.CreateModel(
            name='SurveyQuestionResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(default='No comment.', max_length=280)),
                ('current_as_of', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sur_author', to='stucon.student')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sur_question', to='surveys.surveyquestion')),
                ('survey', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='surveys.survey')),
            ],
            options={
                'unique_together': {('author', 'question', 'survey')},
            },
        ),
        migrations.CreateModel(
            name='PerceptionResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveIntegerField(choices=[(0, 'Strongly Disagree'), (1, 'Disagree'), (2, 'Neutral'), (3, 'Agree'), (4, 'Strongly Agree')])),
                ('current_as_of', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='per_author', to='stucon.student')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='per_question', to='surveys.perceptionquestion')),
                ('subject', models.ForeignKey(default=-1, on_delete=django.db.models.deletion.CASCADE, related_name='per_subject', to='stucon.student')),
                ('survey', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='surveys.survey')),
            ],
            options={
                'unique_together': {('author', 'subject', 'survey', 'question')},
            },
        ),
        migrations.CreateModel(
            name='PeerFeedbackResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('positive_feedback', models.CharField(blank=True, max_length=280, null=True)),
                ('negative_feedback', models.CharField(blank=True, max_length=280, null=True)),
                ('current_as_of', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pf_author', to='stucon.student')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pf_subject', to='stucon.student')),
                ('survey', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='surveys.survey')),
            ],
            options={
                'unique_together': {('author', 'subject', 'survey')},
            },
        ),
        migrations.CreateModel(
            name='NominationResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.CharField(blank=True, max_length=280, null=True)),
                ('current_as_of', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nom_author', to='stucon.student')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surveys.nominationquestion')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nom_subject', to='stucon.student')),
                ('survey', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='surveys.survey')),
            ],
            options={
                'unique_together': {('author', 'question', 'survey')},
            },
        ),
        migrations.CreateModel(
            name='BottomFiveResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_as_of', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bot5_author', to='stucon.student')),
                ('bottom_five_select', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stucon.student')),
                ('survey', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='surveys.survey')),
            ],
            options={
                'unique_together': {('author', 'bottom_five_select', 'survey')},
            },
        ),
    ]
