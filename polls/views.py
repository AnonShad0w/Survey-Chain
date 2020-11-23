import os
import dotenv
import json

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import io
import urllib, base64

from web3 import Web3
from datetime import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.forms import formset_factory
from django.contrib.auth import get_user_model
from django.conf import settings
from pathlib import Path

from .models import Question, Choice, VoterSelection
from .forms import *

# URL of Node Provider Service
url = 'https://ropsten.infura.io/v3/60ccb3c382e44f5b87d4ce6ce0306e57'
web3 = Web3(Web3.HTTPProvider(url))
address = web3.toChecksumAddress('0x070f7B6de5e5453FaCD01dA8cFf382BC6ACd4d9b') #address to deployed smart contract

# Open JSON file
f = open('/home/pi/survey_chain/polls/abi.json', 'r')
abi = json.loads(f.read())
contract = web3.eth.contract(address=address, abi=abi)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

# function based view to check Ethereum Node information
def blockchain_info(request):
    
    current_block_num = web3.eth.blockNumber
    
    if request.method=='GET' and 'current-block-btn' in request.GET:
        tmpl_vars = {
                'current_block_num': current_block_num,
            }
        dataJSON = json.dumps(tmpl_vars)
        tmpl_vars['data'] = dataJSON
        return render(request, 'polls/blockchain.html', tmpl_vars)
        
    if request.method == None:
        pass
    # wallet address from text field
    elif request.method == 'POST':
        address = request.POST.get('address')
        wallet_balance = web3.eth.getBalance(address)
        wallet_balance = web3.fromWei(wallet_balance, "ether") # convert to ether
    
        tmpl_vars = {
            'wallet_balance': wallet_balance,
            'address': address,
        }
        
        return render(request, 'polls/blockchain.html', tmpl_vars)

    return render(request, 'polls/blockchain.html')

class IndexView(generic.ListView):
    
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'
    
    def get_queryset(self):
        """Return the last five published questions
           (not including those set to be published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]
    
class DetailView(generic.DetailView):
    
    model = Question
    template_name = 'polls/detail.html'
    
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())
    
class ResultsView(generic.DetailView):
    
    model = Question
    template_name = 'polls/results.html'
    
    def plot(self):
        plt.plot(range(10))
        fig = plt.gcf()
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = 'data:image/png;base64,' + urllib.parse.quote(string)
        return {'data':uri}

def vote(request, question_id):
    
    question = get_object_or_404(Question, pk=question_id)
    user = request.user
    
    if request.user.is_anonymous:
        return render(request, 'polls/detail.html', {
                'question': question,
                'error_message': "Please login or signup to vote.",
        })
    else:
        try:
            selected_choice = question.choice_set.get(pk=request.POST['choice'])
        except (KeyError, Choice.DoesNotExist):
            # Redisplay the question voting form.
            return render(request, 'polls/detail.html', {
                'question': question,
                'error_message': "You didn't select a choice.",
            })
        # check if the user voted on the question
        if VoterSelection.objects.filter(voter=user, question_id=question_id).exists():
            for choice in question.choice_set.all():
                return render(request, 'polls/detail.html', {
                    'question': question,
                    'error_message': "You already voted on this question.\
                                    Please vote on a dfferent question.",
                })
        
        else:
            VoterSelection.objects.create(choice=selected_choice, voter=user, question_id=question_id)
            selected_choice.votes += 1
            selected_choice.save()
            choice = str(selected_choice)
            print(question)
            print(choice)
            
            key = os.environ['KEY']
            my_wallet_address = '0x34471993D95629D92b47f2e751a7f061F5d8B20e'
            
            transaction = contract.functions.addBallot(choice).buildTransaction()
            transaction.update({ 'gas' : 250000 })
            transaction.update({ 'nonce': web3.eth.getTransactionCount(my_wallet_address) })
            signed_tx = web3.eth.account.signTransaction(transaction, key)
            tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
            receipt = web3.eth.waitForTransactionReceipt(tx_hash)
            block_number = str(receipt['blockNumber'])
            print(receipt['blockNumber'])
            cumulative_gas = str(receipt['cumulativeGasUsed'])
            print(receipt['cumulativeGasUsed'])
            transaction_hash = str((receipt['transactionHash']).hex())
            print(transaction_hash)
            
            request.session['block_number'] = block_number
            request.session['cumulative_gas'] = cumulative_gas
            request.session['transaction_hash'] = transaction_hash
            
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            return HttpResponseRedirect(reverse('polls:detail', args=(question.id,)))

def transaction_detail(request, question_id):

    question = get_object_or_404(Question, pk=question_id)
    user = request.user
    
    block_number = request.session.get('block_number')
    cumulative_gas = request.session.get('cumulative_gas')
    transaction_hash = request.session.get('transaction_hash')
    
    if VoterSelection.objects.filter(voter=user, question_id=question_id).exists():   
        tmpl_vars = {
            'block_number': block_number,
            'cumulative_gas': cumulative_gas,
            'transaction_hash': transaction_hash,
        }
        return render(request, 'polls/transaction.html', tmpl_vars)
        
    else:
        return render(request, 'polls/transaction.html', {
            'question': question,
            'error_message': "You didn't submit a vote for this question yet.",
        })
        
def new_poll(request):
    
    ChoiceFormSet = formset_factory(ChoiceForm, extra=3, min_num=2, validate_min=True)
    question_form = QuestionForm() # when a url is called initially it is GET method so you have to send a instance of form first (empty form)
    choice_form = ChoiceForm()
    
    if request.method == 'POST':
        form = QuestionForm(request.POST or None)
        formset = ChoiceFormSet(request.POST or None, request.FILES)
        if form.is_valid() and formset.is_valid():
            new_poll = form.save(commit=False)
            new_poll.author = request.user
            new_poll.pub_date = timezone.localtime(timezone.now())
            new_poll.save()
            for inline_form in formset:
                if inline_form.cleaned_data:
                    choice = inline_form.save(commit=False)
                    choice.question = new_poll
                    choice.save()
            return redirect('/polls/')
    else:
        form = QuestionForm() # this will return the errors in your form
        formset = ChoiceFormSet()
        
    tmpl_vars = {
        'formset': formset,
        'form': form,
    }
        
    return render(request, 'polls/new.html', tmpl_vars)
