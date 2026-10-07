import json
from datetime import timedelta
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import (
	Category,
	DriverCurrentLocation,
	DriverLocation,
	MenuItem,
	User,
)


class UserAdminPasswordTests(TestCase):
	def test_admin_user_creation_hashes_password(self):
		admin_user = User.objects.create_superuser(
			username='site-admin', password='Admin-test-938!'
		)
		self.client.force_login(admin_user)

		response = self.client.post(reverse('admin:core_user_add'), {
			'username': 'driver-test',
			'password1': 'Quasar-River-871!Memory',
			'password2': 'Quasar-River-871!Memory',
			'email': 'driver@example.test',
			'role': 'driver',
			'phone': '01000000000',
		})

		self.assertEqual(response.status_code, 302)
		driver = User.objects.get(username='driver-test')
		self.assertTrue(driver.check_password('Quasar-River-871!Memory'))


class DriverMenuAccessTests(TestCase):
	def test_driver_sees_active_menu_without_management_actions(self):
		category = Category.objects.create(name='Main dishes', is_active=True)
		MenuItem.objects.create(
			name='Available meal', category=category, price=50, is_active=True
		)
		MenuItem.objects.create(
			name='Hidden meal', category=category, price=60, is_active=False
		)
		inactive_category = Category.objects.create(name='Hidden category', is_active=False)
		MenuItem.objects.create(
			name='Hidden category meal', category=inactive_category, price=70, is_active=True
		)
		driver = User.objects.create_user(
			username='menu-driver', password='Secure!Driver-2837', role='driver'
		)
		self.client.force_login(driver)

		response = self.client.get(reverse('menu_management'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Available meal')
		self.assertNotContains(response, 'Hidden meal')
		self.assertNotContains(response, 'Hidden category')
		self.assertNotContains(response, '/admin/core/menuitem/add/')
		self.assertNotContains(response, '/admin/core/menuitem/1/change/')

	def test_driver_app_formats_last_update_with_english_digits(self):
		driver = User.objects.create_user(
			username='clock-driver', password='Secure!Driver-2837', role='driver'
		)
		self.client.force_login(driver)

		response = self.client.get(reverse('driver_app'))

		self.assertContains(response, "toLocaleTimeString('en-US'")
		self.assertContains(response, 'const [time, meridiem]')
		self.assertContains(response, '`${time} ${meridiem}`')
		self.assertContains(response, 'id="lastUpdate" class="ltr-time" dir="ltr"')


class DriverLocationTrackingTests(TestCase):
	def setUp(self):
		self.driver = User.objects.create_user(
			username='tracking-driver', password='Secure!Driver-2837', role='driver'
		)
		self.admin = User.objects.create_superuser(
			username='tracking-admin', password='Secure!Admin-2837', role='admin'
		)

	def send_location(self, latitude, longitude, accuracy=5):
		return self.client.post(
			reverse('api_driver_location'),
			data=json.dumps({
				'latitude': latitude,
				'longitude': longitude,
				'accuracy': accuracy,
			}),
			content_type='application/json',
		)

	def test_current_location_updates_while_route_is_sampled_every_two_minutes(self):
		self.client.force_login(self.driver)

		first_response = self.send_location(31.2, 29.9)
		current_location = DriverCurrentLocation.objects.get(driver=self.driver)
		self.assertEqual(first_response.status_code, 200)
		self.assertTrue(first_response.json()['history_saved'])
		self.assertEqual(DriverLocation.objects.filter(driver=self.driver).count(), 1)

		DriverCurrentLocation.objects.filter(driver=self.driver).update(
			updated_at=timezone.now() - timedelta(seconds=15)
		)
		second_response = self.send_location(31.21, 29.91)
		current_location.refresh_from_db()
		self.assertEqual(second_response.status_code, 200)
		self.assertFalse(second_response.json()['history_saved'])
		self.assertEqual(current_location.latitude, Decimal('31.21'))
		self.assertEqual(DriverLocation.objects.filter(driver=self.driver).count(), 1)

		DriverCurrentLocation.objects.filter(driver=self.driver).update(
			updated_at=timezone.now() - timedelta(seconds=15)
		)
		DriverLocation.objects.filter(driver=self.driver).update(
			timestamp=timezone.now() - timedelta(minutes=3)
		)
		third_response = self.send_location(31.22, 29.92)

		self.assertEqual(third_response.status_code, 200)
		self.assertTrue(third_response.json()['history_saved'])
		self.assertEqual(DriverLocation.objects.filter(driver=self.driver).count(), 2)

	def test_non_driver_cannot_submit_a_location(self):
		self.client.force_login(self.admin)

		response = self.send_location(31.2, 29.9)

		self.assertEqual(response.status_code, 403)
		self.assertEqual(DriverCurrentLocation.objects.count(), 0)

	def test_out_of_range_coordinates_are_rejected(self):
		self.client.force_login(self.driver)

		response = self.send_location(91, 29.9)

		self.assertEqual(response.status_code, 400)
		self.assertEqual(DriverCurrentLocation.objects.count(), 0)

	def test_low_accuracy_fix_is_shown_live_but_not_saved_to_route(self):
		self.client.force_login(self.driver)

		response = self.send_location(31.2, 29.9, accuracy=2024.8)

		self.assertEqual(response.status_code, 200)
		self.assertTrue(DriverCurrentLocation.objects.filter(driver=self.driver).exists())
		current_location = DriverCurrentLocation.objects.get(driver=self.driver)
		self.assertEqual(current_location.accuracy, 2024.8)
		self.assertFalse(DriverLocation.objects.filter(driver=self.driver).exists())

		self.client.force_login(self.admin)
		map_response = self.client.get(reverse('api_driver_locations'))
		driver_data = next(
			item for item in map_response.json()['drivers'] if item['id'] == self.driver.pk
		)
		self.assertTrue(driver_data['location_is_live'])
		self.assertEqual(driver_data['latest_location']['latitude'], 31.2)

	def test_map_uses_live_location_and_returns_route_oldest_first(self):
		first_point = DriverLocation.objects.create(
			driver=self.driver, latitude=31.1, longitude=29.8, accuracy=5
		)
		second_point = DriverLocation.objects.create(
			driver=self.driver, latitude=31.2, longitude=29.9, accuracy=5
		)
		route_start = timezone.now() - timedelta(minutes=4)
		DriverLocation.objects.filter(pk=first_point.pk).update(timestamp=route_start)
		DriverLocation.objects.filter(pk=second_point.pk).update(
			timestamp=route_start + timedelta(minutes=2)
		)
		DriverCurrentLocation.objects.create(
			driver=self.driver, latitude=31.3, longitude=30.0, accuracy=5
		)
		self.client.force_login(self.admin)

		response = self.client.get(reverse('api_driver_locations'))
		driver_data = next(
			item for item in response.json()['drivers'] if item['id'] == self.driver.pk
		)

		self.assertTrue(driver_data['location_is_live'])
		self.assertEqual(driver_data['latest_location']['latitude'], 31.3)
		self.assertEqual(driver_data['latest_location']['accuracy_m'], 5)
		self.assertEqual(
			[point['latitude'] for point in driver_data['locations']],
			[31.1, 31.2],
		)

	def test_stale_current_location_is_not_reported_as_live(self):
		current_location = DriverCurrentLocation.objects.create(
			driver=self.driver, latitude=31.3, longitude=30.0, accuracy=5
		)
		DriverCurrentLocation.objects.filter(pk=current_location.pk).update(
			updated_at=timezone.now() - timedelta(minutes=2)
		)
		self.client.force_login(self.admin)

		response = self.client.get(reverse('api_driver_locations'))
		driver_data = next(
			item for item in response.json()['drivers'] if item['id'] == self.driver.pk
		)

		self.assertFalse(driver_data['location_is_live'])
