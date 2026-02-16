# Generated manually for creating community management tables

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_achievement_userachievement'),
    ]

    operations = [
        # Create CommunityEvent table
        migrations.CreateModel(
            name='CommunityEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='活动标题')),
                ('description', models.TextField(verbose_name='活动描述')),
                ('status', models.CharField(choices=[('active', '进行中'), ('upcoming', '即将开始'), ('ended', '已结束')], default='upcoming', max_length=20, verbose_name='活动状态')),
                ('image', models.ImageField(blank=True, null=True, upload_to='sys_images/community/community_active_images/', verbose_name='活动图片')),
                ('start_date', models.DateTimeField(blank=True, null=True, verbose_name='开始时间')),
                ('end_date', models.DateTimeField(blank=True, null=True, verbose_name='结束时间')),
                ('location', models.CharField(blank=True, max_length=200, null=True, verbose_name='活动地点')),
                ('participant_count', models.IntegerField(default=0, verbose_name='参与人数')),
                ('prize_info', models.TextField(blank=True, null=True, verbose_name='奖品信息')),
                ('is_pinned', models.BooleanField(default=False, verbose_name='是否置顶')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'db_table': 'community_event',
                'ordering': ['-is_pinned', '-created_at'],
                'verbose_name': '社区活动',
                'verbose_name_plural': '社区活动',
            },
        ),
        
        # Create ReportType table
        migrations.CreateModel(
            name='ReportType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='举报类型名称')),
                ('description', models.TextField(verbose_name='类型描述')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'db_table': 'community_report_type',
                'ordering': ['name'],
                'verbose_name': '举报类型',
                'verbose_name_plural': '举报类型',
            },
        ),
        
        # Create Report table
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_type', models.CharField(choices=[('content', '内容举报'), ('harassment', '骚扰举报'), ('spam', '垃圾信息'), ('inappropriate', '不当行为'), ('other', '其他举报')], max_length=20, verbose_name='举报类型')),
                ('title', models.CharField(max_length=200, verbose_name='举报标题')),
                ('description', models.TextField(verbose_name='举报描述')),
                ('evidence', models.TextField(blank=True, null=True, verbose_name='证据信息')),
                ('status', models.CharField(choices=[('pending', '待处理'), ('reviewing', '审核中'), ('resolved', '已处理'), ('dismissed', '已驳回')], default='pending', max_length=20, verbose_name='处理状态')),
                ('content_type', models.CharField(blank=True, max_length=50, null=True, verbose_name='内容类型')),
                ('content_id', models.IntegerField(blank=True, null=True, verbose_name='内容ID')),
                ('content_title', models.CharField(blank=True, max_length=200, null=True, verbose_name='内容标题')),
                ('review_notes', models.TextField(blank=True, null=True, verbose_name='处理备注')),
                ('action_taken', models.CharField(blank=True, max_length=200, null=True, verbose_name='处理措施')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='举报时间')),
                ('reviewed_at', models.DateTimeField(blank=True, null=True, verbose_name='处理时间')),
                ('resolved_at', models.DateTimeField(blank=True, null=True, verbose_name='解决时间')),
                ('priority', models.IntegerField(choices=[(1, '低'), (2, '中'), (3, '高')], default=1, verbose_name='优先级')),
                ('is_urgent', models.BooleanField(default=False, verbose_name='是否紧急')),
                ('reported_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports_received', to=settings.AUTH_USER_MODEL, verbose_name='被举报人')),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports_made', to=settings.AUTH_USER_MODEL, verbose_name='举报人')),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reports_reviewed', to=settings.AUTH_USER_MODEL, verbose_name='处理人')),
            ],
            options={
                'db_table': 'community_report',
                'ordering': ['-priority', '-created_at'],
                'verbose_name': '举报记录',
                'verbose_name_plural': '举报记录',
            },
        ),
        
        # Create ReportAction table
        migrations.CreateModel(
            name='ReportAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[('warning', '警告'), ('content_removal', '内容删除'), ('account_suspension', '账号暂停'), ('account_ban', '账号封禁'), ('no_action', '无需处理')], max_length=20, verbose_name='处理类型')),
                ('description', models.TextField(verbose_name='处理描述')),
                ('duration', models.IntegerField(blank=True, null=True, verbose_name='持续时间(天)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('executed_at', models.DateTimeField(blank=True, null=True, verbose_name='执行时间')),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='过期时间')),
                ('is_executed', models.BooleanField(default=False, verbose_name='是否已执行')),
                ('is_reverted', models.BooleanField(default=False, verbose_name='是否已撤销')),
                ('executed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='executed_actions', to=settings.AUTH_USER_MODEL, verbose_name='执行人')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='user.report', verbose_name='举报记录')),
            ],
            options={
                'db_table': 'community_report_action',
                'ordering': ['-created_at'],
                'verbose_name': '举报处理措施',
                'verbose_name_plural': '举报处理措施',
            },
        ),
        
        # Create ReportStatistics table
        migrations.CreateModel(
            name='ReportStatistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True, verbose_name='日期')),
                ('total_reports', models.IntegerField(default=0, verbose_name='总举报数')),
                ('pending_reports', models.IntegerField(default=0, verbose_name='待处理举报数')),
                ('resolved_reports', models.IntegerField(default=0, verbose_name='已处理举报数')),
                ('dismissed_reports', models.IntegerField(default=0, verbose_name='已驳回举报数')),
                ('content_reports', models.IntegerField(default=0, verbose_name='内容举报数')),
                ('harassment_reports', models.IntegerField(default=0, verbose_name='骚扰举报数')),
                ('spam_reports', models.IntegerField(default=0, verbose_name='垃圾信息举报数')),
                ('other_reports', models.IntegerField(default=0, verbose_name='其他举报数')),
                ('avg_resolution_time', models.FloatField(default=0.0, verbose_name='平均处理时间(小时)')),
                ('resolution_rate', models.FloatField(default=0.0, verbose_name='处理率')),
            ],
            options={
                'db_table': 'community_report_statistics',
                'ordering': ['-date'],
                'verbose_name': '举报统计',
                'verbose_name_plural': '举报统计',
            },
        ),
    ]