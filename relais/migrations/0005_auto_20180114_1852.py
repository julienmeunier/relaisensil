# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-01-14 18:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('relais', '0004_auto_20171128_0831'),
    ]

    operations = [
        migrations.CreateModel(
            name='People',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30, verbose_name='Prénom')),
                ('last_name', models.CharField(max_length=30, verbose_name='Nom')),
                ('gender', models.CharField(choices=[('H', 'Homme'), ('F', 'Femme')], max_length=1, verbose_name='Sexe')),
                ('birthday', models.DateField(verbose_name='Date de naissance')),
                ('license_nb', models.CharField(blank=True, max_length=30, null=True, verbose_name='Numéro de licence')),
                ('tshirt', models.CharField(blank=True, choices=[('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL')], max_length=4, null=True, verbose_name='Taille tshirt')),
                ('certificat', models.BooleanField(default=False, verbose_name='Certificat médical')),
                ('legal_status', models.BooleanField(default=False, verbose_name='Status légal')),
                ('num', models.PositiveIntegerField(help_text='Pour obtenir les derniers dossards, laisser vide', unique=True, verbose_name='Numéro de dossard')),
                ('time', models.DurationField(blank=True, null=True, verbose_name='Temps')),
                ('ready', models.BooleanField(default=False, verbose_name='Prêt à courir')),
                ('club', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='relais.Club', verbose_name='Club')),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='relais.Company', verbose_name='Entreprise')),
                ('federation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='relais.Federation', verbose_name='Fédération')),
                ('school', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='relais.School', verbose_name='Ecole')),
            ],
            options={
                'verbose_name': 'Personne',
            },
        ),
        migrations.RemoveField(
            model_name='individual',
            name='company',
        ),
        migrations.RemoveField(
            model_name='individual',
            name='payment',
        ),
        migrations.RemoveField(
            model_name='individual',
            name='runner',
        ),
        migrations.RemoveField(
            model_name='team',
            name='company',
        ),
        migrations.RemoveField(
            model_name='team',
            name='payment',
        ),
        migrations.RemoveField(
            model_name='team',
            name='runner_1',
        ),
        migrations.RemoveField(
            model_name='team',
            name='runner_2',
        ),
        migrations.RemoveField(
            model_name='team',
            name='runner_3',
        ),
        migrations.AddField(
            model_name='runner',
            name='category',
            field=models.CharField(choices=[('ADT', 'Adulte'), ('STD', 'Etudiant'), ('ENSIL-ENSCI', 'Etudiant ENSIL-ENSCI'), ('CHA', 'Challenge inter-entreprise'), ('AAEE / AAAEE', "Ancien de l'ENSIL-ENSCI - ENSCI")], default='Adulte', max_length=10, verbose_name='Catégorie du coureur'),
        ),
        migrations.AddField(
            model_name='runner',
            name='email',
            field=models.EmailField(default='', max_length=254, verbose_name='Email'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='runner',
            name='payment',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='relais.Payment', verbose_name='Paiement'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='runner',
            name='team',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name="Nom de l'équipe"),
        ),
        migrations.AlterField(
            model_name='payment',
            name='token',
            field=models.CharField(default='xYkNhVJDZZic', editable=False, max_length=30, verbose_name='Token'),
        ),
        migrations.AlterUniqueTogether(
            name='runner',
            unique_together=set([]),
        ),
        migrations.DeleteModel(
            name='Individual',
        ),
        migrations.DeleteModel(
            name='Team',
        ),
        migrations.RemoveField(
            model_name='runner',
            name='birthday',
        ),
        migrations.RemoveField(
            model_name='runner',
            name='certificat',
        ),
        migrations.RemoveField(
            model_name='runner',
            name='club',
        ),
        migrations.RemoveField(
            model_name='runner',
            name='federation',
        ),
        migrations.RemoveField(
            model_name='runner',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='runner',
            name='gender',
        ),
        migrations.RemoveField(
            model_name='runner',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='runner',
            name='legal_status',
        ),
        migrations.RemoveField(
            model_name='runner',
            name='license_nb',
        ),
        migrations.RemoveField(
            model_name='runner',
            name='num',
        ),
        migrations.RemoveField(
            model_name='runner',
            name='ready',
        ),
        migrations.RemoveField(
            model_name='runner',
            name='school',
        ),
        migrations.RemoveField(
            model_name='runner',
            name='time',
        ),
        migrations.RemoveField(
            model_name='runner',
            name='tshirt',
        ),
        migrations.AddField(
            model_name='runner',
            name='runner_1',
            field=models.OneToOneField(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='runner_1', to='relais.People', verbose_name='1er coureur'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='runner',
            name='runner_2',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='runner_2', to='relais.People', verbose_name='2nd coureur'),
        ),
        migrations.AddField(
            model_name='runner',
            name='runner_3',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='runner_3', to='relais.People', verbose_name='3eme coureur'),
        ),
        migrations.AlterUniqueTogether(
            name='people',
            unique_together=set([('first_name', 'last_name', 'birthday', 'gender')]),
        ),
    ]
