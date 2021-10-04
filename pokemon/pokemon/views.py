from rest_framework.response import Response
from rest_framework.views import APIView
import requests
import random
from collections import defaultdict
attack_val = {'no_damage_to': 0,
              'half_damage_to': 0.5,
              'double_damage_to': 2,
              'no_damage_from': 0,
              'half_damage_from': 0.5,
              'double_damage_from': 2,
              }


def get_damage_dict(pk):
    """ Получает имя покемона и возвращает два словаря первый с уроном от покемона, второй по покемону """
    types_dict = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pk}').json()['types']
    types_url = [i['type']['url'] for i in types_dict]
    damage_dict = [requests.get(j).json()['damage_relations'] for j in types_url]
    damage_to = defaultdict(lambda: 1)
    damage_from = defaultdict(lambda: 1)
    for damage_per_types in damage_dict:
        for key, val in damage_per_types.items():
            for i in val:
                if key[-2:] == 'to':
                    damage_to[i['name']] *= attack_val[key]
                else:
                    damage_from[i['name']] *= attack_val[key]
    return [damage_to, damage_from]


class PokemonTypesDamageView(APIView):
    def get(self, request, pk):
        damage = get_damage_dict(pk)
        return Response({'damage_to':damage[0], 'damage_from': damage[1]})


class PokemonCountersView(APIView):
    def get(self, request, pk):
        damage_types = sorted(get_damage_dict(pk)[1], key=get_damage_dict(pk)[1].get, reverse=True)[:3]
        counters = {}
        for type in damage_types:
            s = random.sample(requests.get(f'https://pokeapi.co/api/v2/type/{type}').json()['pokemon'], 3)
            counters_by_type = [i['pokemon']['name'] for i in s]
            counters[f'Counters with {type} type:'] = counters_by_type
        return Response(counters)


class PokemonBeatView(APIView):
    def get(self, request, pk):
        damage_types = sorted(get_damage_dict(pk)[0], key=get_damage_dict(pk)[0].get, reverse=True)[:3]
        beat = {}
        for type in damage_types:
            s = random.sample(requests.get(f'https://pokeapi.co/api/v2/type/{type}').json()['pokemon'], 3)
            beaten_by_type = [i['pokemon']['name'] for i in s]
            beat[f'Beat pokemon with {type} type. Some examples'] = beaten_by_type
        return Response(beat)
