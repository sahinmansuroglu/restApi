from django.contrib import admin
from .models import Post,Vote
#Admin panelinde gözükecek olan modellerimizi burada register etmeliyiz
# Register your models here.

admin.site.register(Post)

admin.site.register(Vote)