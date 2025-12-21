"""
Plant Database for Home Plant Trainer

Comprehensive database of residential landscape plants with full
condition compatibility, role assignments, and design characteristics.

All plants are selected for home landscape use - no commercial-only species.
"""

from typing import List
from dataclasses import dataclass
from enum import Enum


class PlantRole(Enum):
    """Plant roles in residential landscape design"""
    STRUCTURAL = "structural"
    ACCENT = "accent"
    SCREENING = "screening"
    FOUNDATION_SOFTENER = "foundation_softener"
    EDGE_BORDER = "edge_border"
    GROUNDCOVER = "groundcover"
    CANOPY = "canopy"
    UNDERSTORY = "understory"


class PlantLayer(Enum):
    """Vertical layers in planting design"""
    CANOPY = "canopy"
    UNDERSTORY = "understory"
    SHRUB = "shrub"
    HERBACEOUS = "herbaceous"
    GROUNDCOVER = "groundcover"


class PlantForm(Enum):
    """Plant growth forms"""
    COLUMNAR = "columnar"
    ROUNDED = "rounded"
    MOUNDING = "mounding"
    SPREADING = "spreading"
    VASE = "vase"
    WEEPING = "weeping"
    UPRIGHT = "upright"
    PYRAMIDAL = "pyramidal"


@dataclass
class PlantRecommendation:
    """A single plant with full details for recommendation"""
    botanical_name: str
    common_name: str
    role: PlantRole
    layer: PlantLayer
    form: PlantForm
    mature_height_ft: float
    mature_width_ft: float
    zone_min: int
    zone_max: int
    sun_options: List[str]
    water_options: List[str]
    evergreen: bool
    seasonal_interest: List[str]
    maintenance_level: str
    deer_resistant: bool
    drought_tolerant: bool
    native_regions: List[str]
    design_notes: str


def get_plant_database() -> List[PlantRecommendation]:
    """
    Return the complete plant database for residential landscapes.

    Plants are organized by role and cover zones 3-10 with various
    sun, water, and maintenance requirements.
    """

    plants = []

    # ========================================
    # STRUCTURAL PLANTS (Backbone shrubs)
    # ========================================

    plants.extend([
        PlantRecommendation(
            botanical_name="Buxus sempervirens",
            common_name="American Boxwood",
            role=PlantRole.STRUCTURAL,
            layer=PlantLayer.SHRUB,
            form=PlantForm.ROUNDED,
            mature_height_ft=5.0,
            mature_width_ft=5.0,
            zone_min=5,
            zone_max=9,
            sun_options=["full", "part"],
            water_options=["average"],
            evergreen=True,
            seasonal_interest=["spring", "summer", "fall", "winter"],
            maintenance_level="medium",
            deer_resistant=True,
            drought_tolerant=False,
            native_regions=["Europe", "Asia"],
            design_notes="Classic formal structure plant. Excellent for hedges and foundation."
        ),
        PlantRecommendation(
            botanical_name="Ilex crenata 'Compacta'",
            common_name="Compact Japanese Holly",
            role=PlantRole.STRUCTURAL,
            layer=PlantLayer.SHRUB,
            form=PlantForm.ROUNDED,
            mature_height_ft=4.0,
            mature_width_ft=4.0,
            zone_min=5,
            zone_max=8,
            sun_options=["full", "part", "shade"],
            water_options=["average", "wet"],
            evergreen=True,
            seasonal_interest=["spring", "summer", "fall", "winter"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=False,
            native_regions=["Japan"],
            design_notes="Boxwood alternative with better shade tolerance. Dense habit."
        ),
        PlantRecommendation(
            botanical_name="Taxus x media 'Densiformis'",
            common_name="Dense Spreading Yew",
            role=PlantRole.STRUCTURAL,
            layer=PlantLayer.SHRUB,
            form=PlantForm.SPREADING,
            mature_height_ft=4.0,
            mature_width_ft=6.0,
            zone_min=4,
            zone_max=7,
            sun_options=["full", "part", "shade"],
            water_options=["average"],
            evergreen=True,
            seasonal_interest=["spring", "summer", "fall", "winter"],
            maintenance_level="low",
            deer_resistant=False,
            drought_tolerant=True,
            native_regions=["Hybrid"],
            design_notes="Excellent cold-hardy evergreen structure. Tolerates heavy shade."
        ),
        PlantRecommendation(
            botanical_name="Juniperus chinensis 'Sea Green'",
            common_name="Sea Green Juniper",
            role=PlantRole.STRUCTURAL,
            layer=PlantLayer.SHRUB,
            form=PlantForm.MOUNDING,
            mature_height_ft=5.0,
            mature_width_ft=6.0,
            zone_min=4,
            zone_max=9,
            sun_options=["full"],
            water_options=["dry", "average"],
            evergreen=True,
            seasonal_interest=["spring", "summer", "fall", "winter"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["China"],
            design_notes="Tough, drought-tolerant structure plant. Excellent for hot, dry sites."
        ),
        PlantRecommendation(
            botanical_name="Viburnum x burkwoodii",
            common_name="Burkwood Viburnum",
            role=PlantRole.STRUCTURAL,
            layer=PlantLayer.SHRUB,
            form=PlantForm.ROUNDED,
            mature_height_ft=8.0,
            mature_width_ft=6.0,
            zone_min=4,
            zone_max=8,
            sun_options=["full", "part"],
            water_options=["average"],
            evergreen=False,
            seasonal_interest=["spring", "fall"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=False,
            native_regions=["Hybrid"],
            design_notes="Fragrant spring blooms. Excellent multi-season structure."
        ),
        PlantRecommendation(
            botanical_name="Rhododendron catawbiense",
            common_name="Catawba Rhododendron",
            role=PlantRole.STRUCTURAL,
            layer=PlantLayer.SHRUB,
            form=PlantForm.ROUNDED,
            mature_height_ft=8.0,
            mature_width_ft=8.0,
            zone_min=4,
            zone_max=8,
            sun_options=["part", "shade"],
            water_options=["average", "wet"],
            evergreen=True,
            seasonal_interest=["spring", "summer", "fall", "winter"],
            maintenance_level="medium",
            deer_resistant=False,
            drought_tolerant=False,
            native_regions=["Eastern US"],
            design_notes="Bold evergreen foliage with spectacular spring blooms. Native."
        ),
        PlantRecommendation(
            botanical_name="Prunus laurocerasus 'Otto Luyken'",
            common_name="Otto Luyken Laurel",
            role=PlantRole.STRUCTURAL,
            layer=PlantLayer.SHRUB,
            form=PlantForm.SPREADING,
            mature_height_ft=4.0,
            mature_width_ft=6.0,
            zone_min=6,
            zone_max=9,
            sun_options=["full", "part", "shade"],
            water_options=["average"],
            evergreen=True,
            seasonal_interest=["spring", "summer", "fall", "winter"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Europe"],
            design_notes="Glossy evergreen leaves. Excellent shade-tolerant structure."
        ),
        PlantRecommendation(
            botanical_name="Thuja occidentalis 'Emerald'",
            common_name="Emerald Arborvitae",
            role=PlantRole.STRUCTURAL,
            layer=PlantLayer.SHRUB,
            form=PlantForm.COLUMNAR,
            mature_height_ft=12.0,
            mature_width_ft=4.0,
            zone_min=3,
            zone_max=7,
            sun_options=["full", "part"],
            water_options=["average"],
            evergreen=True,
            seasonal_interest=["spring", "summer", "fall", "winter"],
            maintenance_level="low",
            deer_resistant=False,
            drought_tolerant=False,
            native_regions=["North America"],
            design_notes="Cold-hardy vertical accent. Maintains bright green color in winter."
        ),
    ])

    # ========================================
    # ACCENT PLANTS (Focal points, seasonal color)
    # ========================================

    plants.extend([
        PlantRecommendation(
            botanical_name="Hydrangea macrophylla",
            common_name="Bigleaf Hydrangea",
            role=PlantRole.ACCENT,
            layer=PlantLayer.SHRUB,
            form=PlantForm.MOUNDING,
            mature_height_ft=5.0,
            mature_width_ft=5.0,
            zone_min=5,
            zone_max=9,
            sun_options=["part", "shade"],
            water_options=["average", "wet"],
            evergreen=False,
            seasonal_interest=["summer", "fall"],
            maintenance_level="medium",
            deer_resistant=False,
            drought_tolerant=False,
            native_regions=["Japan"],
            design_notes="Showstopping summer blooms. Needs consistent moisture."
        ),
        PlantRecommendation(
            botanical_name="Hydrangea paniculata 'Limelight'",
            common_name="Limelight Hydrangea",
            role=PlantRole.ACCENT,
            layer=PlantLayer.SHRUB,
            form=PlantForm.UPRIGHT,
            mature_height_ft=8.0,
            mature_width_ft=8.0,
            zone_min=3,
            zone_max=8,
            sun_options=["full", "part"],
            water_options=["average"],
            evergreen=False,
            seasonal_interest=["summer", "fall"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Asia"],
            design_notes="Large lime-green panicles. Cold-hardy and sun-tolerant."
        ),
        PlantRecommendation(
            botanical_name="Rosa 'Knock Out'",
            common_name="Knock Out Rose",
            role=PlantRole.ACCENT,
            layer=PlantLayer.SHRUB,
            form=PlantForm.MOUNDING,
            mature_height_ft=4.0,
            mature_width_ft=4.0,
            zone_min=4,
            zone_max=10,
            sun_options=["full"],
            water_options=["average"],
            evergreen=False,
            seasonal_interest=["spring", "summer", "fall"],
            maintenance_level="low",
            deer_resistant=False,
            drought_tolerant=True,
            native_regions=["Hybrid"],
            design_notes="Continuous bloom with minimal care. Disease-resistant."
        ),
        PlantRecommendation(
            botanical_name="Spiraea japonica 'Goldflame'",
            common_name="Goldflame Spirea",
            role=PlantRole.ACCENT,
            layer=PlantLayer.SHRUB,
            form=PlantForm.MOUNDING,
            mature_height_ft=3.0,
            mature_width_ft=3.0,
            zone_min=4,
            zone_max=8,
            sun_options=["full", "part"],
            water_options=["average"],
            evergreen=False,
            seasonal_interest=["spring", "summer", "fall"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Japan"],
            design_notes="Golden foliage with pink summer flowers. Three-season color."
        ),
        PlantRecommendation(
            botanical_name="Lavandula angustifolia",
            common_name="English Lavender",
            role=PlantRole.ACCENT,
            layer=PlantLayer.HERBACEOUS,
            form=PlantForm.MOUNDING,
            mature_height_ft=2.0,
            mature_width_ft=2.0,
            zone_min=5,
            zone_max=8,
            sun_options=["full"],
            water_options=["dry", "average"],
            evergreen=True,
            seasonal_interest=["summer"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Mediterranean"],
            design_notes="Fragrant silver foliage and purple spikes. Needs good drainage."
        ),
        PlantRecommendation(
            botanical_name="Perovskia atriplicifolia",
            common_name="Russian Sage",
            role=PlantRole.ACCENT,
            layer=PlantLayer.HERBACEOUS,
            form=PlantForm.UPRIGHT,
            mature_height_ft=4.0,
            mature_width_ft=3.0,
            zone_min=4,
            zone_max=9,
            sun_options=["full"],
            water_options=["dry", "average"],
            evergreen=False,
            seasonal_interest=["summer", "fall"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Central Asia"],
            design_notes="Silvery foliage with lavender-blue flower spikes. Heat and drought lover."
        ),
        PlantRecommendation(
            botanical_name="Caryopteris x clandonensis",
            common_name="Blue Mist Shrub",
            role=PlantRole.ACCENT,
            layer=PlantLayer.SHRUB,
            form=PlantForm.MOUNDING,
            mature_height_ft=3.0,
            mature_width_ft=3.0,
            zone_min=5,
            zone_max=9,
            sun_options=["full"],
            water_options=["dry", "average"],
            evergreen=False,
            seasonal_interest=["summer", "fall"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Asia"],
            design_notes="Late summer blue flowers attract butterflies. Silver-gray foliage."
        ),
        PlantRecommendation(
            botanical_name="Hibiscus syriacus",
            common_name="Rose of Sharon",
            role=PlantRole.ACCENT,
            layer=PlantLayer.SHRUB,
            form=PlantForm.UPRIGHT,
            mature_height_ft=10.0,
            mature_width_ft=6.0,
            zone_min=5,
            zone_max=9,
            sun_options=["full", "part"],
            water_options=["average"],
            evergreen=False,
            seasonal_interest=["summer"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Asia"],
            design_notes="Tropical-looking summer blooms on a hardy shrub. Multiple colors."
        ),
    ])

    # ========================================
    # SCREENING PLANTS (Privacy, buffering)
    # ========================================

    plants.extend([
        PlantRecommendation(
            botanical_name="Thuja occidentalis 'Green Giant'",
            common_name="Green Giant Arborvitae",
            role=PlantRole.SCREENING,
            layer=PlantLayer.UNDERSTORY,
            form=PlantForm.PYRAMIDAL,
            mature_height_ft=40.0,
            mature_width_ft=15.0,
            zone_min=5,
            zone_max=8,
            sun_options=["full", "part"],
            water_options=["average"],
            evergreen=True,
            seasonal_interest=["spring", "summer", "fall", "winter"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Hybrid"],
            design_notes="Fast-growing privacy screen. Deer resistant and disease-free."
        ),
        PlantRecommendation(
            botanical_name="Juniperus virginiana",
            common_name="Eastern Red Cedar",
            role=PlantRole.SCREENING,
            layer=PlantLayer.UNDERSTORY,
            form=PlantForm.COLUMNAR,
            mature_height_ft=30.0,
            mature_width_ft=12.0,
            zone_min=3,
            zone_max=9,
            sun_options=["full"],
            water_options=["dry", "average"],
            evergreen=True,
            seasonal_interest=["spring", "summer", "fall", "winter"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Eastern North America"],
            design_notes="Extremely tough native. Tolerates heat, drought, and poor soil."
        ),
        PlantRecommendation(
            botanical_name="Ilex opaca",
            common_name="American Holly",
            role=PlantRole.SCREENING,
            layer=PlantLayer.UNDERSTORY,
            form=PlantForm.PYRAMIDAL,
            mature_height_ft=25.0,
            mature_width_ft=15.0,
            zone_min=5,
            zone_max=9,
            sun_options=["full", "part", "shade"],
            water_options=["average"],
            evergreen=True,
            seasonal_interest=["spring", "summer", "fall", "winter"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=False,
            native_regions=["Eastern US"],
            design_notes="Native evergreen with winter berries. Excellent wildlife value."
        ),
        PlantRecommendation(
            botanical_name="Viburnum dentatum",
            common_name="Arrowwood Viburnum",
            role=PlantRole.SCREENING,
            layer=PlantLayer.SHRUB,
            form=PlantForm.ROUNDED,
            mature_height_ft=10.0,
            mature_width_ft=10.0,
            zone_min=3,
            zone_max=8,
            sun_options=["full", "part", "shade"],
            water_options=["average", "wet"],
            evergreen=False,
            seasonal_interest=["spring", "fall"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=False,
            native_regions=["Eastern North America"],
            design_notes="Native with excellent wildlife value. Blue berries in fall."
        ),
        PlantRecommendation(
            botanical_name="Prunus laurocerasus",
            common_name="Cherry Laurel",
            role=PlantRole.SCREENING,
            layer=PlantLayer.SHRUB,
            form=PlantForm.UPRIGHT,
            mature_height_ft=15.0,
            mature_width_ft=10.0,
            zone_min=6,
            zone_max=9,
            sun_options=["full", "part", "shade"],
            water_options=["average"],
            evergreen=True,
            seasonal_interest=["spring", "summer", "fall", "winter"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Europe"],
            design_notes="Fast-growing evergreen screen. Tolerates heavy shade and pruning."
        ),
        PlantRecommendation(
            botanical_name="Ligustrum japonicum",
            common_name="Japanese Privet",
            role=PlantRole.SCREENING,
            layer=PlantLayer.SHRUB,
            form=PlantForm.UPRIGHT,
            mature_height_ft=12.0,
            mature_width_ft=8.0,
            zone_min=7,
            zone_max=10,
            sun_options=["full", "part"],
            water_options=["dry", "average"],
            evergreen=True,
            seasonal_interest=["spring", "summer", "fall", "winter"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Japan"],
            design_notes="Fast, dense screen for warm climates. Fragrant spring flowers."
        ),
        PlantRecommendation(
            botanical_name="Photinia x fraseri",
            common_name="Red Tip Photinia",
            role=PlantRole.SCREENING,
            layer=PlantLayer.SHRUB,
            form=PlantForm.UPRIGHT,
            mature_height_ft=12.0,
            mature_width_ft=8.0,
            zone_min=7,
            zone_max=9,
            sun_options=["full", "part"],
            water_options=["average"],
            evergreen=True,
            seasonal_interest=["spring", "summer", "fall", "winter"],
            maintenance_level="medium",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Hybrid"],
            design_notes="Brilliant red new growth. Fast screening in warm zones."
        ),
        PlantRecommendation(
            botanical_name="Abelia x grandiflora",
            common_name="Glossy Abelia",
            role=PlantRole.SCREENING,
            layer=PlantLayer.SHRUB,
            form=PlantForm.MOUNDING,
            mature_height_ft=6.0,
            mature_width_ft=6.0,
            zone_min=6,
            zone_max=9,
            sun_options=["full", "part"],
            water_options=["dry", "average"],
            evergreen=True,
            seasonal_interest=["summer", "fall"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Hybrid"],
            design_notes="Long bloom season with fragrant flowers. Butterfly magnet."
        ),
    ])

    # ========================================
    # FOUNDATION SOFTENER PLANTS
    # ========================================

    plants.extend([
        PlantRecommendation(
            botanical_name="Buxus microphylla 'Winter Gem'",
            common_name="Winter Gem Boxwood",
            role=PlantRole.FOUNDATION_SOFTENER,
            layer=PlantLayer.SHRUB,
            form=PlantForm.ROUNDED,
            mature_height_ft=3.0,
            mature_width_ft=3.0,
            zone_min=5,
            zone_max=9,
            sun_options=["full", "part"],
            water_options=["average"],
            evergreen=True,
            seasonal_interest=["spring", "summer", "fall", "winter"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=False,
            native_regions=["Asia"],
            design_notes="Compact evergreen for foundation use. Holds color in winter."
        ),
        PlantRecommendation(
            botanical_name="Nandina domestica 'Compacta'",
            common_name="Compact Heavenly Bamboo",
            role=PlantRole.FOUNDATION_SOFTENER,
            layer=PlantLayer.SHRUB,
            form=PlantForm.UPRIGHT,
            mature_height_ft=4.0,
            mature_width_ft=3.0,
            zone_min=6,
            zone_max=9,
            sun_options=["full", "part", "shade"],
            water_options=["dry", "average"],
            evergreen=True,
            seasonal_interest=["spring", "fall", "winter"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Asia"],
            design_notes="Fine texture with red fall/winter color. Very low maintenance."
        ),
        PlantRecommendation(
            botanical_name="Euonymus japonicus 'Green Spire'",
            common_name="Green Spire Euonymus",
            role=PlantRole.FOUNDATION_SOFTENER,
            layer=PlantLayer.SHRUB,
            form=PlantForm.COLUMNAR,
            mature_height_ft=6.0,
            mature_width_ft=2.0,
            zone_min=6,
            zone_max=9,
            sun_options=["full", "part"],
            water_options=["average"],
            evergreen=True,
            seasonal_interest=["spring", "summer", "fall", "winter"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Japan"],
            design_notes="Narrow vertical form ideal for tight foundation spaces."
        ),
        PlantRecommendation(
            botanical_name="Ilex glabra 'Compacta'",
            common_name="Compact Inkberry",
            role=PlantRole.FOUNDATION_SOFTENER,
            layer=PlantLayer.SHRUB,
            form=PlantForm.ROUNDED,
            mature_height_ft=4.0,
            mature_width_ft=4.0,
            zone_min=4,
            zone_max=9,
            sun_options=["full", "part", "shade"],
            water_options=["average", "wet"],
            evergreen=True,
            seasonal_interest=["spring", "summer", "fall", "winter"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=False,
            native_regions=["Eastern US"],
            design_notes="Native evergreen for wet sites. Boxwood alternative."
        ),
        PlantRecommendation(
            botanical_name="Pittosporum tobira 'Wheelers Dwarf'",
            common_name="Wheeler's Dwarf Pittosporum",
            role=PlantRole.FOUNDATION_SOFTENER,
            layer=PlantLayer.SHRUB,
            form=PlantForm.MOUNDING,
            mature_height_ft=3.0,
            mature_width_ft=4.0,
            zone_min=8,
            zone_max=10,
            sun_options=["full", "part", "shade"],
            water_options=["dry", "average"],
            evergreen=True,
            seasonal_interest=["spring", "summer", "fall", "winter"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Japan"],
            design_notes="Dense mounding form. Excellent for warm climate foundations."
        ),
    ])

    # ========================================
    # EDGE/BORDER PLANTS
    # ========================================

    plants.extend([
        PlantRecommendation(
            botanical_name="Liriope muscari",
            common_name="Big Blue Lilyturf",
            role=PlantRole.EDGE_BORDER,
            layer=PlantLayer.GROUNDCOVER,
            form=PlantForm.MOUNDING,
            mature_height_ft=1.0,
            mature_width_ft=1.0,
            zone_min=5,
            zone_max=10,
            sun_options=["full", "part", "shade"],
            water_options=["dry", "average"],
            evergreen=True,
            seasonal_interest=["summer", "fall"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Asia"],
            design_notes="Tough edging plant for any exposure. Purple flower spikes."
        ),
        PlantRecommendation(
            botanical_name="Carex morrowii 'Ice Dance'",
            common_name="Ice Dance Sedge",
            role=PlantRole.EDGE_BORDER,
            layer=PlantLayer.GROUNDCOVER,
            form=PlantForm.MOUNDING,
            mature_height_ft=1.0,
            mature_width_ft=1.5,
            zone_min=5,
            zone_max=9,
            sun_options=["part", "shade"],
            water_options=["average", "wet"],
            evergreen=True,
            seasonal_interest=["spring", "summer", "fall", "winter"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=False,
            native_regions=["Japan"],
            design_notes="Variegated foliage brightens shade edges. Spreading habit."
        ),
        PlantRecommendation(
            botanical_name="Dianthus gratianopolitanus",
            common_name="Cheddar Pinks",
            role=PlantRole.EDGE_BORDER,
            layer=PlantLayer.HERBACEOUS,
            form=PlantForm.MOUNDING,
            mature_height_ft=0.5,
            mature_width_ft=1.0,
            zone_min=3,
            zone_max=9,
            sun_options=["full"],
            water_options=["dry", "average"],
            evergreen=True,
            seasonal_interest=["spring", "summer"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Europe"],
            design_notes="Silvery foliage, fragrant flowers. Excellent hot, dry edge."
        ),
        PlantRecommendation(
            botanical_name="Nepeta x faassenii",
            common_name="Walker's Low Catmint",
            role=PlantRole.EDGE_BORDER,
            layer=PlantLayer.HERBACEOUS,
            form=PlantForm.MOUNDING,
            mature_height_ft=1.5,
            mature_width_ft=2.0,
            zone_min=4,
            zone_max=8,
            sun_options=["full"],
            water_options=["dry", "average"],
            evergreen=False,
            seasonal_interest=["spring", "summer", "fall"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Hybrid"],
            design_notes="Long bloom season, billowing habit. Pollinator favorite."
        ),
        PlantRecommendation(
            botanical_name="Salvia nemorosa",
            common_name="Woodland Sage",
            role=PlantRole.EDGE_BORDER,
            layer=PlantLayer.HERBACEOUS,
            form=PlantForm.UPRIGHT,
            mature_height_ft=1.5,
            mature_width_ft=1.5,
            zone_min=4,
            zone_max=8,
            sun_options=["full"],
            water_options=["dry", "average"],
            evergreen=False,
            seasonal_interest=["spring", "summer"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Europe"],
            design_notes="Vertical flower spikes. Reblooms if deadheaded."
        ),
    ])

    # ========================================
    # GROUNDCOVER PLANTS
    # ========================================

    plants.extend([
        PlantRecommendation(
            botanical_name="Pachysandra terminalis",
            common_name="Japanese Spurge",
            role=PlantRole.GROUNDCOVER,
            layer=PlantLayer.GROUNDCOVER,
            form=PlantForm.SPREADING,
            mature_height_ft=0.75,
            mature_width_ft=1.5,
            zone_min=4,
            zone_max=8,
            sun_options=["part", "shade"],
            water_options=["average"],
            evergreen=True,
            seasonal_interest=["spring", "summer", "fall", "winter"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=False,
            native_regions=["Japan"],
            design_notes="Classic shade groundcover. Spreads to form dense mat."
        ),
        PlantRecommendation(
            botanical_name="Vinca minor",
            common_name="Periwinkle",
            role=PlantRole.GROUNDCOVER,
            layer=PlantLayer.GROUNDCOVER,
            form=PlantForm.SPREADING,
            mature_height_ft=0.5,
            mature_width_ft=2.0,
            zone_min=4,
            zone_max=9,
            sun_options=["full", "part", "shade"],
            water_options=["dry", "average"],
            evergreen=True,
            seasonal_interest=["spring"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Europe"],
            design_notes="Vigorous spreader with blue spring flowers. Very adaptable."
        ),
        PlantRecommendation(
            botanical_name="Heuchera villosa",
            common_name="Hairy Alumroot",
            role=PlantRole.GROUNDCOVER,
            layer=PlantLayer.HERBACEOUS,
            form=PlantForm.MOUNDING,
            mature_height_ft=1.0,
            mature_width_ft=1.5,
            zone_min=4,
            zone_max=9,
            sun_options=["part", "shade"],
            water_options=["average"],
            evergreen=True,
            seasonal_interest=["spring", "summer", "fall"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Eastern US"],
            design_notes="Native with colorful foliage. Heat tolerant heuchera."
        ),
        PlantRecommendation(
            botanical_name="Ajuga reptans",
            common_name="Bugleweed",
            role=PlantRole.GROUNDCOVER,
            layer=PlantLayer.GROUNDCOVER,
            form=PlantForm.SPREADING,
            mature_height_ft=0.5,
            mature_width_ft=1.5,
            zone_min=3,
            zone_max=9,
            sun_options=["full", "part", "shade"],
            water_options=["average", "wet"],
            evergreen=True,
            seasonal_interest=["spring"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=False,
            native_regions=["Europe"],
            design_notes="Fast-spreading with blue flower spikes. Purple-leaved forms."
        ),
        PlantRecommendation(
            botanical_name="Sedum spurium",
            common_name="Two Row Stonecrop",
            role=PlantRole.GROUNDCOVER,
            layer=PlantLayer.GROUNDCOVER,
            form=PlantForm.SPREADING,
            mature_height_ft=0.5,
            mature_width_ft=2.0,
            zone_min=3,
            zone_max=9,
            sun_options=["full"],
            water_options=["dry", "average"],
            evergreen=True,
            seasonal_interest=["summer", "fall"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Caucasus"],
            design_notes="Succulent for hot, dry areas. Red fall color."
        ),
        PlantRecommendation(
            botanical_name="Phlox subulata",
            common_name="Creeping Phlox",
            role=PlantRole.GROUNDCOVER,
            layer=PlantLayer.GROUNDCOVER,
            form=PlantForm.SPREADING,
            mature_height_ft=0.5,
            mature_width_ft=2.0,
            zone_min=3,
            zone_max=9,
            sun_options=["full"],
            water_options=["dry", "average"],
            evergreen=True,
            seasonal_interest=["spring"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Eastern US"],
            design_notes="Spring flower carpet in many colors. Native."
        ),
    ])

    # ========================================
    # CANOPY TREES (Residential scale)
    # ========================================

    plants.extend([
        PlantRecommendation(
            botanical_name="Acer rubrum",
            common_name="Red Maple",
            role=PlantRole.CANOPY,
            layer=PlantLayer.CANOPY,
            form=PlantForm.ROUNDED,
            mature_height_ft=50.0,
            mature_width_ft=40.0,
            zone_min=3,
            zone_max=9,
            sun_options=["full", "part"],
            water_options=["average", "wet"],
            evergreen=False,
            seasonal_interest=["spring", "fall"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=False,
            native_regions=["Eastern North America"],
            design_notes="Native with brilliant fall color. Adaptable to many soils."
        ),
        PlantRecommendation(
            botanical_name="Quercus palustris",
            common_name="Pin Oak",
            role=PlantRole.CANOPY,
            layer=PlantLayer.CANOPY,
            form=PlantForm.PYRAMIDAL,
            mature_height_ft=60.0,
            mature_width_ft=40.0,
            zone_min=4,
            zone_max=8,
            sun_options=["full"],
            water_options=["average", "wet"],
            evergreen=False,
            seasonal_interest=["fall"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=False,
            native_regions=["Eastern US"],
            design_notes="Fast-growing native oak. Excellent structure and fall color."
        ),
        PlantRecommendation(
            botanical_name="Zelkova serrata",
            common_name="Japanese Zelkova",
            role=PlantRole.CANOPY,
            layer=PlantLayer.CANOPY,
            form=PlantForm.VASE,
            mature_height_ft=50.0,
            mature_width_ft=50.0,
            zone_min=5,
            zone_max=8,
            sun_options=["full"],
            water_options=["average"],
            evergreen=False,
            seasonal_interest=["fall"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Japan"],
            design_notes="Elm substitute with vase shape. Very urban tolerant."
        ),
        PlantRecommendation(
            botanical_name="Lagerstroemia indica x fauriei",
            common_name="Hybrid Crape Myrtle",
            role=PlantRole.CANOPY,
            layer=PlantLayer.UNDERSTORY,
            form=PlantForm.VASE,
            mature_height_ft=25.0,
            mature_width_ft=20.0,
            zone_min=6,
            zone_max=10,
            sun_options=["full"],
            water_options=["dry", "average"],
            evergreen=False,
            seasonal_interest=["summer", "fall", "winter"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Hybrid"],
            design_notes="Long summer bloom, ornamental bark. Multi-trunk or single."
        ),
        PlantRecommendation(
            botanical_name="Magnolia grandiflora 'Little Gem'",
            common_name="Little Gem Magnolia",
            role=PlantRole.CANOPY,
            layer=PlantLayer.UNDERSTORY,
            form=PlantForm.PYRAMIDAL,
            mature_height_ft=25.0,
            mature_width_ft=15.0,
            zone_min=7,
            zone_max=9,
            sun_options=["full", "part"],
            water_options=["average"],
            evergreen=True,
            seasonal_interest=["spring", "summer", "fall", "winter"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=False,
            native_regions=["Southeastern US"],
            design_notes="Compact evergreen magnolia with fragrant white flowers."
        ),
    ])

    # ========================================
    # UNDERSTORY TREES
    # ========================================

    plants.extend([
        PlantRecommendation(
            botanical_name="Cornus florida",
            common_name="Flowering Dogwood",
            role=PlantRole.UNDERSTORY,
            layer=PlantLayer.UNDERSTORY,
            form=PlantForm.ROUNDED,
            mature_height_ft=25.0,
            mature_width_ft=25.0,
            zone_min=5,
            zone_max=9,
            sun_options=["part", "shade"],
            water_options=["average"],
            evergreen=False,
            seasonal_interest=["spring", "fall"],
            maintenance_level="medium",
            deer_resistant=False,
            drought_tolerant=False,
            native_regions=["Eastern US"],
            design_notes="Iconic native understory tree. Spring flowers, fall color, winter berries."
        ),
        PlantRecommendation(
            botanical_name="Acer palmatum",
            common_name="Japanese Maple",
            role=PlantRole.UNDERSTORY,
            layer=PlantLayer.UNDERSTORY,
            form=PlantForm.ROUNDED,
            mature_height_ft=20.0,
            mature_width_ft=20.0,
            zone_min=5,
            zone_max=8,
            sun_options=["part", "shade"],
            water_options=["average"],
            evergreen=False,
            seasonal_interest=["spring", "summer", "fall"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=False,
            native_regions=["Japan"],
            design_notes="Elegant form and foliage. Numerous cultivars for different effects."
        ),
        PlantRecommendation(
            botanical_name="Amelanchier x grandiflora",
            common_name="Apple Serviceberry",
            role=PlantRole.UNDERSTORY,
            layer=PlantLayer.UNDERSTORY,
            form=PlantForm.VASE,
            mature_height_ft=20.0,
            mature_width_ft=15.0,
            zone_min=4,
            zone_max=8,
            sun_options=["full", "part"],
            water_options=["average"],
            evergreen=False,
            seasonal_interest=["spring", "summer", "fall"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["North America"],
            design_notes="Four-season interest: flowers, fruit, fall color, bark. Native."
        ),
        PlantRecommendation(
            botanical_name="Cercis canadensis",
            common_name="Eastern Redbud",
            role=PlantRole.UNDERSTORY,
            layer=PlantLayer.UNDERSTORY,
            form=PlantForm.ROUNDED,
            mature_height_ft=25.0,
            mature_width_ft=25.0,
            zone_min=4,
            zone_max=9,
            sun_options=["full", "part"],
            water_options=["average"],
            evergreen=False,
            seasonal_interest=["spring", "fall"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Eastern US"],
            design_notes="Native with spectacular spring bloom on bare branches."
        ),
        PlantRecommendation(
            botanical_name="Chionanthus virginicus",
            common_name="White Fringetree",
            role=PlantRole.UNDERSTORY,
            layer=PlantLayer.UNDERSTORY,
            form=PlantForm.ROUNDED,
            mature_height_ft=20.0,
            mature_width_ft=20.0,
            zone_min=4,
            zone_max=9,
            sun_options=["full", "part"],
            water_options=["average"],
            evergreen=False,
            seasonal_interest=["spring"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=False,
            native_regions=["Eastern US"],
            design_notes="Fragrant fringe-like white flowers in late spring. Native."
        ),
        PlantRecommendation(
            botanical_name="Vitex agnus-castus",
            common_name="Chaste Tree",
            role=PlantRole.UNDERSTORY,
            layer=PlantLayer.UNDERSTORY,
            form=PlantForm.VASE,
            mature_height_ft=15.0,
            mature_width_ft=15.0,
            zone_min=6,
            zone_max=9,
            sun_options=["full"],
            water_options=["dry", "average"],
            evergreen=False,
            seasonal_interest=["summer"],
            maintenance_level="low",
            deer_resistant=True,
            drought_tolerant=True,
            native_regions=["Mediterranean"],
            design_notes="Blue flower spikes in summer. Heat and drought tolerant."
        ),
    ])

    return plants


def get_plants_by_role(role: PlantRole) -> List[PlantRecommendation]:
    """Get all plants for a specific role"""
    database = get_plant_database()
    return [p for p in database if p.role == role]


def get_plants_by_zone(zone: int) -> List[PlantRecommendation]:
    """Get all plants compatible with a specific zone"""
    database = get_plant_database()
    return [p for p in database if p.zone_min <= zone <= p.zone_max]


def get_plants_by_conditions(
    zone: int,
    sun: str,
    water: str,
    max_height: float = 100.0
) -> List[PlantRecommendation]:
    """Get plants matching specific site conditions"""
    database = get_plant_database()
    results = []

    for plant in database:
        # Zone check
        if not (plant.zone_min <= zone <= plant.zone_max):
            continue
        # Sun check
        if sun not in plant.sun_options:
            continue
        # Water check
        if water not in plant.water_options:
            continue
        # Height check
        if plant.mature_height_ft > max_height:
            continue

        results.append(plant)

    return results


def search_plants(query: str) -> List[PlantRecommendation]:
    """Search plants by name"""
    database = get_plant_database()
    query_lower = query.lower()

    return [
        p for p in database
        if query_lower in p.common_name.lower()
        or query_lower in p.botanical_name.lower()
    ]


if __name__ == "__main__":
    # Test database
    database = get_plant_database()
    print(f"Total plants in database: {len(database)}")

    # Count by role
    from collections import Counter
    role_counts = Counter(p.role.value for p in database)
    print("\nPlants by role:")
    for role, count in sorted(role_counts.items()):
        print(f"  {role}: {count}")

    # Test zone filter
    zone_7_plants = get_plants_by_zone(7)
    print(f"\nPlants for zone 7: {len(zone_7_plants)}")

    # Test condition filter
    condition_match = get_plants_by_conditions(
        zone=6,
        sun="part",
        water="average",
        max_height=8.0
    )
    print(f"Plants for zone 6, part sun, average water, under 8ft: {len(condition_match)}")
