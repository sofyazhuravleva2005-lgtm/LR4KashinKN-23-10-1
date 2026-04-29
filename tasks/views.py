import os
import random
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.shortcuts import render
from django.conf import settings

def run_pdp_simulation():
    # Считываем секретные ключи (задаются в Secrets Replit)
    s1 = os.environ.get('IMP_S1_KASHIN', 'не задан')
    s2 = os.environ.get('IMP_S2_KASHIN', 'не задан')
    s3 = os.environ.get('IMP_S3_KASHIN', 'не задан')

    num_requests = 16
    threshold = int(os.environ.get('THRESHOLD', 95))
    risk_lst = []
    decision_lst = []

    for i in range(1, num_requests + 1):
        token_mismatch = random.randint(0, 35)
        ip_mismatch = random.randint(0, 30)
        device_mismatch = random.randint(0, 25)
        replay_detected = random.randint(0, 45)

        base_risk = 8
        weighted_risk = (token_mismatch * 1.3 + ip_mismatch * 1.1 +
                         device_mismatch * 1.0 + replay_detected * 1.6)
        risk = round(base_risk + weighted_risk)
        risk_lst.append(risk)

        decision = "Blocked" if risk > threshold else "Allowed"
        decision_lst.append(decision)

    table = list(zip(range(1, num_requests + 1), risk_lst, decision_lst))
    tframe = pd.DataFrame(table, columns=['Запрос №', 'Риск подмены', 'Решение'])

    # Генерация графиков
    static_dir = os.path.join(settings.BASE_DIR, 'tasks', 'static', 'tasks')
    os.makedirs(static_dir, exist_ok=True)

    plt.figure(figsize=(10, 5))
    plt.bar(tframe['Запрос №'], tframe['Риск подмены'], color='skyblue')
    plt.xlabel('Номер запроса')
    plt.ylabel('Риск подмены (0-100)')
    plt.title('Риск подмены доверенного пользователя')
    plt.grid(axis='y')
    plt.savefig(os.path.join(static_dir, 'risk_bar.png'))
    plt.close()

    blocked_count = decision_lst.count("Blocked")
    allowed_count = decision_lst.count("Allowed")
    plt.figure()
    plt.pie([allowed_count, blocked_count], labels=['Allowed', 'Blocked'],
            autopct='%1.1f%%', shadow=True, startangle=90,
            colors=['lightgreen', 'salmon'])
    plt.title('Распределение решений ПДП-Контейнера')
    plt.savefig(os.path.join(static_dir, 'decision_pie.png'))
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.plot(tframe['Запрос №'], tframe['Риск подмены'], marker='o', color='red')
    plt.xlabel('Номер запроса')
    plt.ylabel('Риск подмены')
    plt.title('Тренд риска подмены')
    plt.grid()
    plt.savefig(os.path.join(static_dir, 'risk_trend.png'))
    plt.close()

    return {
        'table_html': tframe.to_html(classes='table table-striped', index=False),
        'total_requests': num_requests,
        'blocked': blocked_count,
        'allowed': allowed_count,
        'chart_paths': {
            'bar': 'tasks/risk_bar.png',
            'pie': 'tasks/decision_pie.png',
            'line': 'tasks/risk_trend.png',
        },
        'secrets': {'s1': s1, 's2': s2, 's3': s3},
    }

def index(request):
    data = run_pdp_simulation()
    return render(request, 'index.html', data)