from rest_framework import serializers
from boards.models import Board, Topic
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    boards = serializers.PrimaryKeyRelatedField(many=True, queryset=Board.objects.all())

    class Meta:
        model = User
        fields = ('username', 'email', 'boards',)


class BoardSerializer(serializers.ModelSerializer):
    creater = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Board
        fields = ('id', 'name', 'description', 'creater', 'is_deleted',)

    def create(self, validated_data):

        return Board.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.is_deleted = validated_data.get('is_deleted', instance.is_deleted)
        instance.save()
        return instance


class TopicSerializer(serializers.ModelSerializer):
    starter = serializers.StringRelatedField(read_only=True)
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())

    class Meta:
        model = Topic
        fields = ('subject', 'board', 'last_updated', 'starter', 'views')

    def create(self, validated_data):
        return Topic.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.subject = validated_data.get('subject', instance.subject)
        instance.board = validated_data.get('board', instance.board)
        instance.starter = validated_data.get('starter', instance.starter)
        instance.last_update = validated_data.get('last_updated', instance.last_updated)
        instance.save()
        return instance
