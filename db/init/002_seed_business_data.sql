INSERT INTO business_data(order_id, customer_name, status, status_code, progress_percentage, details, expected_completion, last_update)
VALUES
('4200000001', 'Schneider Electric', '制作中', '02', 50, '订单正在生产中，预计还需要 2-3 天完成', '2026-01-24', '2026-01-21 10:30:00'),
('4200000002', 'Schneider Electric', '已完成', '03', 100, '订单已完成并进入待发运状态', '2026-01-20', '2026-01-20 15:00:00'),
('4200000003', 'Schneider Electric', '待排产', '01', 10, '订单已接收，等待生产排期', '2026-01-28', '2026-01-22 09:00:00')
ON CONFLICT (order_id) DO NOTHING;
