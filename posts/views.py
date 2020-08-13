from django.shortcuts import render
from rest_framework import generics,permissions,mixins,status
from rest_framework.response import Response
from rest_framework.exceptions import  ValidationError
from .models import Post,Vote
from .serializers import PostSerializer,VoteSerializer

#Aşağıda ListCreateAPIView değilde sadece ListAPIView olsaydı api sadece listeleme yapar ekleme yapamazdı

class PostList(generics.ListCreateAPIView):
    queryset=Post.objects.all()
    serializer_class=PostSerializer #serializer.py dosyasında oluşturulan sınıf
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]# giriş yapılmadıysa sadece okur

    # bu func ismi değişmeyecek rest apiye hangi kullanıcının kayıt yapacağını gözterecek
    def perform_create(self,serializer):
        serializer.save(poster=self.request.user)


#RetrieveDestroyAPIView read ve delete için kullanılıt
class PostRetrieveDestroy(generics.RetrieveDestroyAPIView):
    queryset=Post.objects.all()
    serializer_class=PostSerializer #serializer.py dosyasında oluşturulan sınıf
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]

    #aşağıdaki method silme öncesi kontrolyapıyor post'un sahibi olup olmadığımızı
    # eğer bu func olmazsa silem olur ancak kontrolsüz olur
    def delete(self,request,*args, **kwargs):
        post= Post.objects.filter(pk=self.kwargs['pk'],poster=self.request.user)
        if post.exists():
            return self.destroy(request,*args,**kwargs)
        else:
            raise ValidationError('This isn\'t your post to delete')




# Eğer Apide sioy silmede yapıalacaksa DestroyModelMixin de parametre olarak girilmeli ve delete fun'ı
# ' yazılmalı
# bu api sadece oylama işlemi yapar post ile get işlemi yapmaz
class VoteCreate(generics.CreateAPIView,mixins.DestroyModelMixin):
    serializer_class=VoteSerializer #serializer.py dosyasında oluşturulan sınıf
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]# giriş yapılmadıysa sadece okur

    # query seti oluşturabilmek için o anki user'i ve post edilecek gönderi öğrenilip ona göre query seti oluşturuldu.
    # döndürülecek olan sorgu ancak CreateApıview olarak ayarlandığı için sadece api içinden erişilir
    # dışardan erişilemez
    def get_queryset(self):
        user=self.request.user
        post=Post.objects.get(pk=self.kwargs['pk'])
        return Vote.objects.filter(voter=user,post=post)

    def perform_create(self,serializer):
        if self.get_queryset().exists():
            raise ValidationError('You have already voted for this post :)')
        serializer.save(voter=self.request.user,post=Post.objects.get(pk=self.kwargs['pk']))

    def delete(self,request,*args, **kwargs):
         if self.get_queryset().exists():
             self.get_queryset().delete()
             return Response(status=status.HTTP_204_NO_CONTENT)
         else:
             raise ValidationError('You never voted for this post')

             