from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import PerfilCorretor, LogAtividade


@receiver(post_save, sender=User)
def criar_perfil_corretor(sender, instance, created, **kwargs):
    if created:
        PerfilCorretor.objects.get_or_create(user=instance)


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    LogAtividade.objects.create(
        usuario=user,
        acao='login',
        modelo='Sistema',
        descricao='Fez login no painel',
    )