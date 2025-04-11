from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Ad, ExchangeProposal
from .forms import AdForm, ExchangeProposalForm
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Q

@login_required
def create_ad(request):
    if request.method == 'POST':
        form = AdForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            return redirect('ad_detail', ad_id=ad.id)
    else:
        form = AdForm()
    return render(request, 'ads/create_ad.html', {'form': form})


def ad_list(request):
    ads_list = Ad.objects.all().order_by('-created_at')

    # Фильтрация
    category = request.GET.get('category')
    condition = request.GET.get('condition')

    if category:
        ads_list = ads_list.filter(category=category)
    if condition:
        ads_list = ads_list.filter(condition=condition)

    # Поиск
    search_query = request.GET.get('q')
    if search_query:
        ads_list = ads_list.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Пагинация
    paginator = Paginator(ads_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'ads/ad_list.html', {
        'ads': page_obj,  # Передаём и ads, и page_obj для совместимости
        'page_obj': page_obj,
        'categories': Ad.objects.values_list('category', flat=True).distinct(),
    })


def ad_detail(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    return render(request, 'ads/ad_detail.html', {'ad': ad})


@login_required
def edit_ad(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)

    # Проверяем, что пользователь — автор объявления
    if ad.user != request.user:
        return HttpResponseForbidden("У вас нет прав для редактирования этого объявления!")

    if request.method == 'POST':
        form = AdForm(request.POST, instance=ad)
        if form.is_valid():
            form.save()
            return redirect('ad_detail', ad_id=ad.id)
    else:
        form = AdForm(instance=ad)  # Форма с текущими данными объявления

    return render(request, 'ads/edit_ad.html', {'form': form, 'ad': ad})


@login_required
def delete_ad(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    if ad.user != request.user:
        return HttpResponseForbidden("Вы не автор этого объявления!")
    ad.delete()
    return redirect('ad_list')


@login_required
def create_proposal(request, ad_receiver_id):
    ad_receiver = get_object_or_404(Ad, id=ad_receiver_id)
    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.ad_sender = get_object_or_404(Ad, user=request.user)
            proposal.ad_receiver = ad_receiver
            proposal.save()
            return redirect('ad_detail', ad_id=ad_receiver.id)
    else:
        form = ExchangeProposalForm()
    return render(request, 'ads/create_proposal.html', {'form': form, 'ad': ad_receiver})


@login_required
def manage_proposal(request, proposal_id, action):
    proposal = get_object_or_404(ExchangeProposal, id=proposal_id)

    if proposal.ad_receiver.user != request.user:
        return HttpResponseForbidden("Недостаточно прав!")

    if action in ['accept', 'reject']:
        proposal.status = 'accepted' if action == 'accept' else 'rejected'
        proposal.save()

    return redirect('ad_detail', ad_id=proposal.ad_receiver.id)



