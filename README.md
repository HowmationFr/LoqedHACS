# LOQED Smart Lock - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Intégration Home Assistant pour la serrure connectée **LOQED Touch Smart Lock**, via l'API locale du bridge.

## Fonctionnalités

- **Entité Lock** : verrouiller (night lock), déverrouiller (day lock / loquet), ouvrir (open)
- **Capteurs** : batterie (%), tension batterie, signal Wi-Fi, signal Bluetooth, état du verrou
- **Binary sensor** : connectivité de la serrure
- **Communication 100% locale** via le bridge LOQED (pas de cloud)
- **Polling** toutes les 10 secondes

## Prérequis

- Un bridge LOQED connecté à votre réseau local
- L'adresse IP du bridge
- Le `local_key_id` et le `secret` (disponibles dans [app.loqed.com](https://app.loqed.com) → API → API Keys)

## Installation via HACS

1. Dans HACS, allez dans **Intégrations** → menu **⋮** → **Dépôts personnalisés**
2. Ajoutez l'URL du dépôt avec la catégorie **Intégration**
3. Cherchez "LOQED" et installez
4. Redémarrez Home Assistant
5. Allez dans **Paramètres** → **Appareils et services** → **Ajouter une intégration** → **LOQED Smart Lock**

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

## Entités créées

| Entité | Type | Description |
|--------|------|-------------|
| `lock.<nom>` | Lock | Contrôle principal de la serrure |
| `sensor.<nom>_battery` | Sensor | Niveau de batterie en % |
| `sensor.<nom>_battery_voltage` | Sensor | Tension batterie (désactivé par défaut) |
| `sensor.<nom>_bolt_state` | Sensor | État du verrou (open / day_lock / night_lock) |
| `sensor.<nom>_wifi_signal` | Sensor | Force du signal Wi-Fi (désactivé par défaut) |
| `sensor.<nom>_bluetooth_signal` | Sensor | Force du signal BLE (désactivé par défaut) |
| `binary_sensor.<nom>_lock_online` | Binary Sensor | Connectivité de la serrure |

## Licence

MIT
