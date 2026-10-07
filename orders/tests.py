from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import json
from core.models import Category, MenuItem, Order, OrderItem, User


class DriverAssignmentTests(TestCase):
	def setUp(self):
		self.admin = User.objects.create_user(
			username='admin', password='test-password', role='admin'
		)
		self.driver = User.objects.create_user(
			username='driver', password='test-password', role='driver'
		)
		self.kitchen_user = User.objects.create_user(
			username='kitchen', password='test-password', role='kitchen'
		)
		self.order = Order.objects.create(daily_serial=1, customer_name='Test customer')
		self.category = Category.objects.create(name='Main dishes')
		self.menu_item = MenuItem.objects.create(
			name='Meal', category=self.category, price=100
		)

	def test_admin_can_assign_active_driver(self):
		self.client.force_login(self.admin)

		response = self.client.post(
			reverse('order_assign_driver', args=[self.order.pk]),
			{'driver_id': self.driver.pk},
		)

		self.assertRedirects(response, reverse('order_detail', args=[self.order.pk]))
		self.order.refresh_from_db()
		self.assertEqual(self.order.driver, self.driver)
		self.assertEqual(self.order.status, 'ready')

	def test_ajax_assignment_returns_without_redirecting(self):
		self.client.force_login(self.admin)

		response = self.client.post(
			reverse('order_assign_driver', args=[self.order.pk]),
			{'driver_id': self.driver.pk},
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['status'], 'success')

	def test_admin_cannot_change_driver_after_order_is_delivered(self):
		self.order.status = 'delivered'
		self.order.driver = self.driver
		self.order.save()
		self.client.force_login(self.admin)

		response = self.client.post(
			reverse('order_assign_driver', args=[self.order.pk]),
			{'driver_id': self.driver.pk},
		)

		self.assertEqual(response.status_code, 400)
		self.order.refresh_from_db()
		self.assertEqual(self.order.driver, self.driver)
		self.assertEqual(self.order.status, 'delivered')

	def test_delivered_order_shows_driver_without_assignment_controls(self):
		self.order.status = 'delivered'
		self.order.driver = self.driver
		self.order.save()
		self.client.force_login(self.admin)

		for route_name in ('dashboard', 'order_list', 'order_detail'):
			url = reverse(route_name, args=[self.order.pk]) if route_name == 'order_detail' else reverse(route_name)
			response = self.client.get(url)
			self.assertEqual(response.status_code, 200)
			self.assertContains(response, self.driver.username)
			self.assertNotContains(response, f'/orders/{self.order.pk}/assign-driver/')

	def test_kitchen_user_cannot_be_assigned_as_driver(self):
		self.client.force_login(self.admin)

		response = self.client.post(
			reverse('order_assign_driver', args=[self.order.pk]),
			{'driver_id': self.kitchen_user.pk},
		)

		self.assertEqual(response.status_code, 404)
		self.order.refresh_from_db()
		self.assertIsNone(self.order.driver)

	def test_driver_cannot_update_unassigned_order(self):
		self.order.status = 'ready'
		self.order.save()
		self.client.force_login(self.driver)

		response = self.client.post(
			reverse('order_update_status', args=[self.order.pk]),
			{'status': 'delivering'},
		)

		self.assertEqual(response.status_code, 403)
		self.order.refresh_from_db()
		self.assertEqual(self.order.status, 'ready')

	def test_assigned_driver_can_start_and_complete_delivery(self):
		self.order.driver = self.driver
		self.order.status = 'ready'
		self.order.save()
		self.client.force_login(self.driver)

		start_response = self.client.post(
			reverse('order_update_status', args=[self.order.pk]),
			{'status': 'delivering'},
		)
		self.assertEqual(start_response.status_code, 200)

		delivery_response = self.client.post(
			reverse('order_update_status', args=[self.order.pk]),
			{'status': 'delivered'},
		)
		self.assertEqual(delivery_response.status_code, 200)
		self.order.refresh_from_db()
		self.assertEqual(self.order.status, 'delivered')
		self.assertIsNotNone(self.order.delivered_at)

	def test_driver_sees_only_assigned_orders(self):
		self.order.driver = self.driver
		self.order.save()
		other_order = Order.objects.create(daily_serial=2, customer_name='Other customer')
		self.client.force_login(self.driver)

		response = self.client.get(reverse('order_list'))

		self.assertEqual(list(response.context['orders']), [self.order])
		self.assertNotContains(response, other_order.customer_name)

	def test_driver_cannot_edit_or_create_orders(self):
		self.client.force_login(self.driver)

		edit_response = self.client.get(reverse('order_edit', args=[self.order.pk]))
		create_response = self.client.get(reverse('order_create'))

		self.assertEqual(edit_response.status_code, 403)
		self.assertEqual(create_response.status_code, 403)

	def test_driver_app_lists_assigned_orders_only(self):
		self.order.driver = self.driver
		self.order.save()
		other_order = Order.objects.create(daily_serial=2, customer_name='Other customer')
		self.client.force_login(self.driver)

		response = self.client.get(reverse('driver_app'))

		self.assertContains(response, 'Test customer')
		self.assertNotContains(response, other_order.customer_name)

	def test_staff_can_assign_driver_from_order_list(self):
		self.client.force_login(self.admin)

		response = self.client.get(reverse('order_list'))

		self.assertContains(response, 'driver-assign-form')
		self.assertContains(response, f'action="{reverse("order_assign_driver", args=[self.order.pk])}"')

	def test_order_detail_marks_current_status_button(self):
		self.order.status = 'ready'
		self.order.save()
		self.client.force_login(self.admin)

		response = self.client.get(reverse('order_detail', args=[self.order.pk]))

		self.assertContains(response, 'class="btn btn-success" aria-pressed="true" onclick="updateStatus(\'ready\')"')
		self.assertContains(response, 'class="btn btn-outline-secondary" aria-pressed="false" onclick="updateStatus(\'new\')"')

	def test_staff_can_assign_driver_from_dashboard(self):
		self.client.force_login(self.admin)

		response = self.client.get(reverse('dashboard'))

		self.assertContains(response, 'driver-assign-form')
		self.assertContains(response, f'action="{reverse("order_assign_driver", args=[self.order.pk])}"')

	def test_dashboard_order_number_has_items_preview(self):
		OrderItem.objects.create(
			order=self.order,
			menu_item=self.menu_item,
			quantity=2,
			regular_price=100,
			price=100,
		)
		self.client.force_login(self.admin)

		response = self.client.get(reverse('dashboard'))

		self.assertContains(response, f'data-order-preview="order-items-{self.order.pk}"')
		self.assertContains(response, 'Meal × 2')

	def test_dashboard_order_number_and_customer_link_to_order(self):
		self.client.force_login(self.admin)

		response = self.client.get(reverse('dashboard'))
		order_url = f'href="{reverse("order_detail", args=[self.order.pk])}"'

		self.assertContains(response, order_url, count=3)

	def test_dashboard_defaults_to_last_24_hours_and_can_show_all(self):
		Order.objects.filter(pk=self.order.pk).update(
			created_at=timezone.now() - timedelta(hours=25)
		)
		self.client.force_login(self.admin)

		recent_response = self.client.get(reverse('dashboard'))
		all_response = self.client.get(reverse('dashboard'), {'range': 'all'})

		self.assertEqual(recent_response.context['order_range'], '24h')
		self.assertEqual(recent_response.context['page_obj'].paginator.count, 0)
		self.assertEqual(all_response.context['order_range'], 'all')
		self.assertEqual(all_response.context['page_obj'].paginator.count, 1)

	def test_dashboard_paginates_all_orders_by_thirty(self):
		for serial in range(2, 32):
			Order.objects.create(daily_serial=serial, customer_name=f'Customer {serial}')
		self.client.force_login(self.admin)

		first_page = self.client.get(reverse('dashboard'), {'range': 'all'})
		second_page = self.client.get(reverse('dashboard'), {'range': 'all', 'page': 2})

		self.assertEqual(first_page.context['page_obj'].paginator.count, 31)
		self.assertEqual(len(first_page.context['recent_orders']), 30)
		self.assertEqual(len(second_page.context['recent_orders']), 1)

	def test_order_creation_applies_discount_per_unit_before_quantity(self):
		self.client.force_login(self.admin)

		response = self.client.post(reverse('order_create'), {
			'customer_id': 'new',
			'customer_name': 'VIP customer',
			'customer_phone': '01000000000',
			'customer_address': 'Test address',
			'delivery_fee': '10',
			'items_data': json.dumps([
				{'id': self.menu_item.pk, 'quantity': 2, 'discount': 4},
			]),
		})

		created_order = Order.objects.exclude(pk=self.order.pk).get()
		item = created_order.items.get()
		self.assertEqual(response.status_code, 302)
		self.assertEqual(item.regular_price, 100)
		self.assertEqual(item.price, 96)
		self.assertEqual(item.subtotal, 192)
		self.assertEqual(created_order.subtotal, 192)
		self.assertEqual(created_order.discount_total, 8)
		self.assertEqual(created_order.total, 202)

	def test_order_edit_preserves_base_price_and_applies_discount_per_unit(self):
		OrderItem.objects.create(
			order=self.order,
			menu_item=self.menu_item,
			quantity=1,
			regular_price=100,
			price=80,
		)
		self.client.force_login(self.admin)

		response = self.client.post(reverse('order_edit', args=[self.order.pk]), {
			'customer_id': 'new',
			'customer_name': 'VIP customer',
			'customer_phone': '01000000000',
			'customer_address': 'Test address',
			'delivery_fee': '5',
			'items_data': json.dumps([
				{'id': self.menu_item.pk, 'quantity': 2, 'discount': 30},
			]),
		})

		self.order.refresh_from_db()
		item = self.order.items.get()
		self.assertEqual(response.status_code, 302)
		self.assertEqual(item.regular_price, 100)
		self.assertEqual(item.price, 70)
		self.assertEqual(self.order.subtotal, 140)
		self.assertEqual(self.order.discount_total, 60)
		self.assertEqual(self.order.total, 145)

	def test_discount_over_base_price_is_rejected_without_creating_order(self):
		self.client.force_login(self.admin)

		response = self.client.post(reverse('order_create'), {
			'customer_id': 'new',
			'customer_name': 'VIP customer',
			'items_data': json.dumps([
				{'id': self.menu_item.pk, 'quantity': 1, 'discount': 101},
			]),
		})

		self.assertEqual(response.status_code, 400)
		self.assertEqual(Order.objects.count(), 1)

	def test_fractional_discount_is_rejected(self):
		self.client.force_login(self.admin)

		response = self.client.post(reverse('order_create'), {
			'customer_id': 'new',
			'customer_name': 'VIP customer',
			'items_data': json.dumps([
				{'id': self.menu_item.pk, 'quantity': 1, 'discount': 4.5},
			]),
		})

		self.assertEqual(response.status_code, 400)
		self.assertEqual(Order.objects.count(), 1)

	def test_discount_column_is_hidden_until_order_has_discount(self):
		item = OrderItem.objects.create(
			order=self.order,
			menu_item=self.menu_item,
			quantity=1,
			regular_price=100,
			price=100,
		)
		self.client.force_login(self.admin)

		for route_name in ('order_detail', 'order_print'):
			response = self.client.get(reverse(route_name, args=[self.order.pk]))
			self.assertNotContains(response, 'خصم الوحدة')
			self.assertNotContains(response, 'سعر القائمة')
			self.assertNotContains(response, 'سعر البيع')

		item.price = 96
		item.save()
		self.order.items.update(subtotal=96)
		self.order.subtotal = 96
		self.order.total = 96
		self.order.save()

		for route_name in ('order_detail', 'order_print'):
			response = self.client.get(reverse(route_name, args=[self.order.pk]))
			self.assertContains(response, 'الخصم')
			self.assertContains(response, 'إجمالي الخصم')
