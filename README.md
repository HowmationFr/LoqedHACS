# LOQED Local - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Intégration Home Assistant pour le contrôle **100% local** de la serrure connectée **LOQED Touch Smart Lock**, via l'API locale du bridge.

> **Note :** Cette intégration fonctionne en parallèle de l'intégration officielle LOQED (cloud). Elle utilise le domaine `loqed_local` et crée un appareil séparé suffixé "(Local)". Vous pouvez utiliser les deux simultanément.

## Fonctionnalités

- **Entité Lock** : verrouiller (night lock), déverrouiller (day lock / loquet), ouvrir (open)
- **Capteurs** : batterie (%), tension batterie, signal Wi-Fi, signal Bluetooth, état du verrou
- **Binary sensor** : connectivité de la serrure
- **Communication 100% locale** via le bridge LOQED (pas de cloud, pas d'internet requis)
- **Polling** toutes les 10 secondes
- **Coexiste** avec l'intégration officielle LOQED

## Prérequis

- Un bridge LOQED connecté à votre réseau local
- L'adresse IP du bridge
- Le `local_key_id` et le `secret` (disponibles dans [app.loqed.com](https://app.loqed.com) → API → API Keys)

## Installation via HACS

1. Dans HACS, allez dans **Intégrations** → menu **⋮** → **Dépôts personnalisés**
2. Ajoutez l'URL du dépôt avec la catégorie **Intégration**
3. Cherchez "LOQED Local" et installez
4. Redémarrez Home Assistant
5. Allez dans **Paramètres** → **Appareils et services** → **Ajouter une intégration** → **LOQED Local**

## Configuration

| Champ | Description | Exemple |
|-------|-------------|---------|
| Nom de la serrure | Nom affiché dans HA | `Porte d'entrée` |
| Adresse IP du bridge | IP locale du bridge | `10.0.10.29` |
| ID de la clé locale | `local_key_id` de l'API | `6` |
| Secret | Clé API en base64 | `9UvugMX5ozDk...` |

## Comportement du verrou

| Action HA | Commande LOQED | Description |
|-----------|----------------|-------------|
| **Verrouiller** | `NIGHT_LOCK` | Verrouillage complet |
| **Déverrouiller** | `DAY_LOCK` | Position loquet (déverrouillé mais fermé) |
| **Ouvrir** | `OPEN` | Ouverture complète (déverrouillage + rétraction du pêne) |

## Différences avec l'intégration officielle LOQED

| | LOQED (officielle) | LOQED Local (cette intégration) |
|---|---|---|
| Communication | Cloud | Réseau local uniquement |
| Dépendance internet | Oui | Non |
| Latence | Variable | ~instantanée |
| Domaine HA | `loqed` | `loqed_local` |

## Licence

MIT
