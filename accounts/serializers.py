from .models import CustomUser
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True)

	class Meta:
		model = CustomUser
		fields =['username','password','nickname']

	def create(self, validated_data):
		password = validated_data.pop('password')
		user = CustomUser.objects.create(**validated_data) # 패스워드 벨리데이터 설정을 해야하나 현재 정의하지 않아서 조건이 없음.
		user.set_password(password) #패스워드 해싱처리
		user.save()
		return user