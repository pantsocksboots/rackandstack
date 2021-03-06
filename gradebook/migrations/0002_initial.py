# Generated by Django 4.0 on 2022-01-24 06:04

from django.db import migrations, models
import django.db.models.deletion
import gradebook.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('gradebook', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('rubric', '0001_initial'),
        ('stucon', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='traitscore',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trait_student', to='stucon.student'),
        ),
        migrations.AddField(
            model_name='traitscore',
            name='trait',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rubric.trait'),
        ),
        migrations.AddField(
            model_name='objectivescore',
            name='evolution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rubric.evolution', validators=[gradebook.models.is_objective]),
        ),
        migrations.AddField(
            model_name='objectivescore',
            name='grader',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='obj_grader', to='auth.user'),
        ),
        migrations.AddField(
            model_name='objectivescore',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='obj_student', to='stucon.student'),
        ),
        migrations.AlterUniqueTogether(
            name='traitscore',
            unique_together={('student', 'evolution', 'trait', 'grader')},
        ),
        migrations.AlterUniqueTogether(
            name='objectivescore',
            unique_together={('student', 'evolution')},
        ),
    ]
