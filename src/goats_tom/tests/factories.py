"""
This module contains factory classes for creating instances of various models
used in the application, particularly for testing purposes.
"""
import factory
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.utils import timezone
from goats_tom.models import GOALogin, Key, ProgramKey, TaskProgress, UserKey
from tom_dataproducts.models import DataProduct, ReducedDatum
from tom_observations.tests.factories import ObservingRecordFactory
from tom_targets.tests.factories import SiderealTargetFactory


class UserFactory(factory.django.DjangoModelFactory):
    """Factory class for creating `User` model instances for testing.

    Attributes
    ----------
    username : factory.Sequence
        Generates a unique username sequence for each user instance.
    password : str
        A hashed password, generated using `make_password` for consistency in
        tests.
    """

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    password = make_password("password")


class GOALoginFactory(factory.django.DjangoModelFactory):
    """Factory for creating GOALogin instances for testing."""

    class Meta:
        model = GOALogin
        skip_postgeneration_save = True

    user = factory.SubFactory(UserFactory)
    username = factory.Sequence(lambda n: f"testuser{n}")
    password = "default_password"


class TaskProgressFactory(factory.django.DjangoModelFactory):
    # Factory for creating TaskProgress instances for testing.
    class Meta:
        model = TaskProgress

    task_id = factory.Faker("uuid4")
    progress = factory.Sequence(lambda n: n % 100)
    status = "running"
    done = False
    start_time = factory.LazyFunction(timezone.now)
    end_time = None
    error_message = None
    user = factory.SubFactory(UserFactory)


class DataProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DataProduct

    product_id = factory.Faker("uuid4")
    target = factory.SubFactory(SiderealTargetFactory)
    # Ensure observation_record is associated with the same target as
    # DataProduct
    observation_record = factory.SubFactory(
        ObservingRecordFactory, target_id=factory.SelfAttribute("..target.id")
    )
    data = ContentFile(b"some data", name="data.txt")
    extra_data = factory.Faker("text")
    data_product_type = "photometry"
    featured = False


class ReducedDatumFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReducedDatum
        skip_postgeneration_save = True

    target = factory.SubFactory(SiderealTargetFactory)
    data_product = factory.SubFactory(DataProductFactory)
    data_type = "photometry"
    source_name = "TOM Toolkit"
    source_location = "TOM-TOM Direct Sharing"
    timestamp = factory.LazyFunction(timezone.now)
    value = factory.LazyFunction(
        lambda: {"magnitude": 15.582, "filter": "r", "error": 0.005}
    )

    @factory.post_generation
    def message(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for message in extracted:
                self.message.add(message)


class KeyFactory(factory.django.DjangoModelFactory):
    """Base factory for keys."""

    class Meta:
        model = Key
        abstract = True

    user = factory.SubFactory(UserFactory)
    password = "default_password"
    site = factory.Iterator(["GS", "GN"])


class UserKeyFactory(KeyFactory):
    """Factory for UserKey model."""

    class Meta:
        model = UserKey

    email = factory.LazyAttribute(lambda obj: f"{obj.user.username}@example.com")
    is_active = False


class ProgramKeyFactory(KeyFactory):
    """Factory for ProgramKey model."""

    class Meta:
        model = ProgramKey

    program_id = factory.Sequence(lambda n: f"GN-2024A-Q-{n}")
