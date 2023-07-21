from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers
from .models import *
from django.db.models import Q
from django.contrib.auth.models import Group

# User Serializer
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

# Register Serializer
class RegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])
        return user

        
class RegistrationSerializer(ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2'] 
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def save(self):
        account = User(
            email = self.validated_data['email'],
            username = self.validated_data['username'],
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        account.set_password(password)
        account.save()
        return account

        
class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class ArtistSerializer(ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'


class SongSerializer(ModelSerializer):
    artists = SerializerMethodField()

    def get_artists(self, song):
        artists = Artist.objects.filter(Q(mainartist__song=song) | Q(collabartist__song=song)).distinct()
        return [artist.name for artist in artists]

    class Meta:
        model = Song
        fields = ('name', 'artists')


class PlaylistSerializer(ModelSerializer):
    songs = SerializerMethodField()
    status = SerializerMethodField()

    def get_songs(self, playlist):
        return [song.name for song in playlist.songs.all()]

    def get_status(self, playlist):
        return 'public' if playlist.status == 'pub' else 'private'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['songs'] = self.get_songs(instance)
        return representation

    class Meta:
        model = Playlist
        fields = ['name', 'status', 'songs']


class PlayedSongSerializer(ModelSerializer):
    song_name = serializers.CharField(source='song.name', read_only=True)
    artist_name = serializers.SerializerMethodField()

    def get_artist_name(self, played_song):
        artists = Artist.objects.filter(Q(mainartist__song=played_song.song) | Q(collabartist__song=played_song.song)).distinct()
        return [artist.name for artist in artists]

    class Meta:
        model = PlayedSong
        fields = ['song_name', 'artist_name']


class UserPlayedSongSerializer(ModelSerializer):
    song_name = serializers.CharField(source='played_song.song.name', read_only=True)
    artist_name = serializers.SerializerMethodField()

    def get_artist_name(self, user_played_song):
        artists = Artist.objects.filter(Q(mainartist__song=user_played_song.played_song.song) | Q(collabartist__song=user_played_song.played_song.song)).distinct()
        return [artist.name for artist in artists]
    
    class Meta:
        model = UserPlayedSong
        fields = ['song_name', 'artist_name']


class PlayedPlaylistSerializer(serializers.ModelSerializer):
    playlist_name = serializers.CharField(source='playlist.name', read_only=True)
    songs = serializers.SerializerMethodField()

    def get_songs(self, played_playlist):
        song_data = []
        for song in played_playlist.playlist.songs.all():
            artists = Artist.objects.filter(Q(mainartist__song=song) | Q(collabartist__song=song)).distinct()
            artist_data = [artist.name for artist in artists]
            song_data.append({
                'song_name': song.name,
                'artist_names': artist_data
            })
        return song_data

    class Meta:
        model = PlayedPlaylist
        fields = ['playlist_name', 'songs']



class UserPlayedPlaylistSerializer(ModelSerializer):
    playlist_name = serializers.CharField(source='played_playlist.playlist.name', read_only=True)
    songs = serializers.SerializerMethodField()

    def get_songs(self, user_played_playlist):
        song_data = []
        for song in user_played_playlist.played_playlist.playlist.songs.all():
            artists = Artist.objects.filter(Q(mainartist__song=song) | Q(collabartist__song=song)).distinct()
            artist_data = [artist.name for artist in artists]
            song_data.append({
                'song_name': song.name,
                'artist_names': artist_data
            })
        return song_data
    
    class Meta:
        model = UserPlayedPlaylist
        fields = ['playlist_name', 'songs']
