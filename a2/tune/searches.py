from search.minimax import Minimax
from evaluate.dijkstra import Dijkstra

searches = {
    'sanity-check': {
        'baseline': Minimax(1, None, Dijkstra(), False, False),
        'size': 3,
        'N': { 'min': 100, 'max': 10000 },
        'Cp': { 'min': 1.4, 'max': 1.4 },
        'num-configs': 20,
        'confidence-threshold': 1.0
    },
    'cp-range': {
        'baseline': Minimax(3, None, Dijkstra(), False, False),
        'size': 3,
        'N': { 'min': 5000, 'max': 5000 },
        'Cp': { 'min': 0.5, 'max': 2.0 },
        'num-configs': 100,
        'confidence-threshold': 1.0
    },
    'n-range': {
        'baseline': Minimax(3, None, Dijkstra(), False, False),
        'size': 3,
        'N': { 'min': 100, 'max': 10000 },
        'Cp': { 'min': 1.4, 'max': 1.4 },
        'num-configs': 100,
        'confidence-threshold': 1.0
    },
    'n-vs-cp': {
        'baseline': Minimax(3, None, Dijkstra(), False, False),
        'size': 3,
        'N': { 'min': 100, 'max': 10000 },
        'Cp': { 'min': 0.5, 'max': 2.0 },
        'num-configs': 250,
        'confidence-threshold': 1.0
    }
}