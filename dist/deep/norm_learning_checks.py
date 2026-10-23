"""Teaching checks only: temporal masking, gradient reversal, trapezoidal area.
No dataset access and no model training. Requires an existing PyTorch environment.
"""
import argparse
import json
from pathlib import Path
import torch


class Reverse(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, scale):
        ctx.scale = scale
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad):
        return -ctx.scale * grad, None


def temporal_masks(batch, modalities, length, kind, generator):
    mask = torch.ones(batch, modalities, length, 1)
    for b in range(batch):
        selected = range(modalities) if kind == 1 else [int(torch.randint(modalities, (1,), generator=generator))]
        for m in selected:
            width = int(torch.randint(length // 2 + 1, (1,), generator=generator))
            start = int(torch.randint(length - width + 1, (1,), generator=generator))
            mask[b, m, start:start + width] = 0
    return mask


def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument('--output', default='norm_checks.json')
    out = Path(args.parse_args().output)
    result = {'scope': 'synthetic teaching checks; not a NORM-TR reproduction'}
    for kind in (1, 2):
        g = torch.Generator().manual_seed(7)
        mask = temporal_masks(4, 3, 8, kind, g)
        assert mask.shape == (4, 3, 8, 1)
        assert torch.all((mask == 0) | (mask == 1))
        widths = (mask[..., 0] == 0).sum(-1)
        assert int(widths.max()) <= 4
        for b in range(4):
            if kind == 2:
                assert int((widths[b] > 0).sum()) <= 1
            for m in range(3):
                zeros = torch.where(mask[b, m, :, 0] == 0)[0]
                if len(zeros) > 1:
                    assert torch.all(zeros[1:] - zeros[:-1] == 1)
        x = torch.arange(4 * 3 * 8 * 2, dtype=torch.float32).reshape(4, 3, 8, 2)
        y = x * mask
        assert y.shape == x.shape
        assert torch.equal(y[mask.expand_as(x) == 1], x[mask.expand_as(x) == 1])
        result[f'type_{kind}_erased_widths'] = widths.tolist()
    gradients = {}
    for scale in (0., .5, 1.):
        z = torch.tensor(2., requires_grad=True)
        d = torch.tensor(1., requires_grad=True)
        loss = (d * Reverse.apply(z, scale)) ** 2
        loss.backward()
        assert torch.isclose(z.grad, torch.tensor(-4 * scale))
        assert torch.isclose(d.grad, torch.tensor(8.))
        gradients[str(scale)] = {'extractor_grad': z.grad.item(), 'discriminator_grad': d.grad.item()}
    result['grl'] = gradients
    rates, scores = [0., .5, 1.], [.8, .6, .2]
    area = sum((scores[i] + scores[i + 1]) / 2 * (rates[i + 1] - rates[i]) for i in range(2))
    assert abs(area - .55) < 1e-9
    result['synthetic_auilc'] = area
    result['passed'] = True
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
