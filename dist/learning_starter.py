"""学习练习；合成数据结果不是科研实验。只加载自己可信的本地数据或权重。"""
import argparse
import json
import pickle
from datetime import datetime
from pathlib import Path
import numpy as np
import torch


def inspect_data(path):
    with open(path, 'rb') as f:
        data = pickle.load(f)
    result = {}
    for split in ['train', 'valid', 'test']:
        part = data[split]
        result[split] = {'fields': list(part), 'shapes': {}}
        for key in ['text_bert', 'vision', 'audio', 'regression_labels']:
            a = np.asarray(part[key])
            result[split]['shapes'][key] = {'shape': list(a.shape), 'dtype': str(a.dtype),
                                           'finite': bool(np.isfinite(a).all())}
        ids = [str(x) for x in part['id']]
        result[split]['duplicate_ids'] = len(ids) - len(set(ids))
        if split == 'train':
            result[split]['first_three'] = [{'id': ids[i], 'label': np.asarray(part['regression_labels'][i]).tolist()} for i in range(min(3, len(ids)))]
    print(json.dumps(result, ensure_ascii=False, indent=2))


def math_demo():
    y = torch.tensor([-1., 0., 1.])
    pred = torch.tensor([-.6, .2, .7])
    w = torch.tensor(1., requires_grad=True)
    ((w * 2 - 6) ** 2).backward()
    a = torch.softmax(torch.tensor([0., np.log(3.)]), dim=-1).float()
    v = torch.tensor([[2., 0.], [0., 4.]])
    print(json.dumps({'MAE': (pred-y).abs().mean().item(), 'gradient': w.grad.item(),
                      'updated_w_lr_0.01': (w-.01*w.grad).item(),
                      'attention': a.tolist(), 'weighted_value': (a@v).tolist()}, indent=2))


def model():
    return torch.nn.Sequential(torch.nn.Linear(4, 16), torch.nn.Tanh(), torch.nn.Linear(16, 1))


def train():
    torch.manual_seed(8)
    torch.set_num_threads(1)
    x = torch.randn(32, 4)
    y = x[:, :1]*2-x[:, 1:2]+.3
    net = model()
    opt = torch.optim.Adam(net.parameters(), lr=.02)
    history = []
    for step in range(501):
        net.train()
        opt.zero_grad(set_to_none=True)
        loss = torch.nn.functional.mse_loss(net(x), y)
        if step % 100 == 0:
            history.append({'step': step, 'mse': loss.item()})
        if step < 500:
            loss.backward()
            opt.step()
    net.eval()
    with torch.no_grad():
        expected = net(x)
    out = Path(__file__).resolve().parent / ('toy_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    out.mkdir(parents=True, exist_ok=False)
    torch.save({'weights': net.state_dict(), 'x': x, 'y': y, 'expected': expected}, out/'toy.pt')
    report = {'kind': 'synthetic training-loop exercise', 'history': history, 'checkpoint': str(out/'toy.pt')}
    (out/'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


def reload(path):
    # 本地 PyTorch 1.13 兼容；仅使用本练习自己生成的权重。
    saved = torch.load(path, map_location='cpu')
    net = model()
    net.load_state_dict(saved['weights'])
    net.eval()
    with torch.no_grad():
        prediction = net(saved['x'])
    delta = (prediction-saved['expected']).abs().max().item()
    assert delta < 1e-6, '重新加载后的预测不一致'
    print(json.dumps({'max_prediction_difference': delta, 'passed': True}))


def metrics():
    # R[i,j]：完成阶段 i 后，在场景 j 的成绩；未学场景留 NaN。
    r = np.array([[80., np.nan, np.nan], [65., 78., np.nan], [60., 70., 76.]])
    aa = np.mean(r[-1])
    bwt = np.mean([r[-1,j]-r[j,j] for j in range(2)])
    forgetting = np.mean([np.nanmax(r[j:,j])-r[-1,j] for j in range(2)])
    print(json.dumps({'teaching_matrix_percent': [[None if np.isnan(x) else x for x in row] for row in r],
                      'AA_percent': aa, 'BWT_percentage_points': bwt, 'F_percentage_points': forgetting}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('task', choices=['inspect', 'math', 'train', 'reload', 'metrics'])
    parser.add_argument('--data')
    parser.add_argument('--checkpoint')
    args = parser.parse_args()
    if args.task == 'inspect':
        if not args.data: parser.error('inspect 需要 --data')
        inspect_data(args.data)
    elif args.task == 'reload':
        if not args.checkpoint: parser.error('reload 需要 --checkpoint')
        reload(args.checkpoint)
    elif args.task == 'math': math_demo()
    elif args.task == 'train': train()
    else: metrics()
