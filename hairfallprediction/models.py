from django.contrib.auth.models import User
from django.db import models
from PIL import Image
from django.urls import reverse
from django.utils.text import slugify


class HairfallData(models.Model):

    gender = models.IntegerField()
    age = models.IntegerField()
    hairline_pattern = models.IntegerField()
    hair_fall_rate = models.IntegerField()
    nutrition = models.IntegerField()
    chemical_product_usage = models.IntegerField()
    genetics = models.IntegerField()
    past_chronic_illness = models.IntegerField()
    sleep_disturbance = models.IntegerField()
    water_quality_issue = models.IntegerField()
    stress = models.IntegerField()
    food_habit = models.IntegerField()
    hormonal_changes = models.IntegerField()
    hair_care_habits = models.IntegerField()
    smoking = models.IntegerField()
    label = models.IntegerField()  # Risk level label

    class Meta:
        db_table = 'hairfall_data'


def get_default_author():
    return User.objects.get(username='hridaya').id


class Product(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    name = models.CharField(max_length=500)
    slug = models.SlugField(unique=True, max_length=200)  # Increased to 200 characters
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    feedback = models.TextField()
    details = models.TextField()
    image = models.ImageField(default='default_user.jpg', upload_to='product_images/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    stock = models.PositiveIntegerField(default=0)  # New stock column added
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='products',
        default=get_default_author
    )

    def __str__(self):
        return f"{self.name} - {self.status}"

    def get_absolute_url(self):
        return reverse('recom-product-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            # Truncate if too long (adjust as needed)
            if len(base_slug) > 180:  # Leave room for uniqueness suffixes
                base_slug = base_slug[:180]
            self.slug = base_slug

            # Ensure uniqueness if needed
            original_slug = self.slug
            counter = 1
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        # Check if no image is uploaded and set the default image
        if not self.image:
            self.image = 'product_images/default_user.jpg'

        super().save(*args, **kwargs)  # Call the parent class's save method

        # Resize image if needed
        if self.image and self.image != 'product_images/default_user.jpg':
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)

    class Meta:
        db_table = 'products'

