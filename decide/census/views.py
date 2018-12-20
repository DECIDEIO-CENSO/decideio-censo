from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import User
from voting.models import Voting
from rest_framework import generics
from django.shortcuts import render, get_object_or_404,HttpResponse
from census import serializers
from rest_framework.response import Response
from django.views.generic import TemplateView
from rest_framework.status import (
        HTTP_201_CREATED as ST_201,
        HTTP_204_NO_CONTENT as ST_204,
        HTTP_400_BAD_REQUEST as ST_400,
        HTTP_401_UNAUTHORIZED as ST_401,
        HTTP_409_CONFLICT as ST_409
)

from base.perms import UserIsStaff
from .models import Census
from voting.models import Voting
from django.contrib.auth.models import User

class CensusView(TemplateView):
    template_name = 'census/census.html'
    
def selectVoting(request):
    votings= set()
    allVotings = Census.objects.all().values_list('voting_id', flat=True)
    for v in allVotings:
          votings.add(Voting.objects.filter(id=v)[0])
    return render(request,'census/selectVoting.html', {'votings':votings})

def listVoters(request):
        voting_id = request.GET.get('voting_id')
        voters = set()
        voter_ids = Census.objects.filter(voting_id=voting_id).values_list('voter_id', flat=True)
        print(voter_ids)
        for v_id in voter_ids:
            voters.add(User.objects.filter(id=v_id)[0])    
        return render(request, 'census/censusByVoting.html', {'voters': voters,'voting_id':voting_id})

def create(request):
   
    votings = Voting.objects.all()
    allUsers = User.objects.all()
    
    return render(request,'census/create.html', {'allUsers':allUsers, 'votings':votings})

def create2(request):
    voting_id = request.POST.get('voting')
    voters = request.POST.getlist('voters')
    print(voters)
    for voter in voters:
        census = Census(voting_id=voting_id, voter_id=voter)
        census.save()
    
    template = loader.get_template('census/index.html')
    context = {
        
        }
    
    return HttpResponse(template.render(context, request))


class CensusCreate(generics.ListCreateAPIView):
    #permission_classes = (UserIsStaff,)
    serializer_class = serializers.CensusSerializer

    def create(self, request, *args, **kwargs):
        voting_id = request.data.get('voting_id')
        voters = request.data.get('voters')
        try:
            for voter in voters:
                census = Census(voting_id=voting_id, voter_id=voter)
                census.save()
        except IntegrityError:
            return Response('Error try to create census', status=ST_409)
        return Response('Census created', status=ST_201)

    def list(self, request, *args, **kwargs):
        voting_id = request.GET.get('voting_id')
        voters = Census.objects.filter(voting_id=voting_id).values_list('voter_id', flat=True)
        return Response({'voters': voters})


class CensusDetail(generics.RetrieveDestroyAPIView):

    def destroy(self, request, voting_id, *args, **kwargs):
        voters = request.data.get('voters')
        census = Census.objects.filter(voting_id=voting_id, voter_id__in=voters)
        census.delete()
        return Response('Voters deleted from census', status=ST_204)

    def retrieve(self, request, voting_id, *args, **kwargs):
        voter = request.GET.get('voter_id')
        try:
            Census.objects.get(voting_id=voting_id, voter_id=voter)
        except ObjectDoesNotExist:
            return Response('Invalid voter', status=ST_401)
        return Response('Valid voter')
