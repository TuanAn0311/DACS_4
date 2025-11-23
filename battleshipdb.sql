-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th10 23, 2025 lúc 04:14 AM
-- Phiên bản máy phục vụ: 8.4.0
-- Phiên bản PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `battleshipdb`
--

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `lich_su_tran_dau`
--

CREATE TABLE `lich_su_tran_dau` (
  `MaTranDau` int NOT NULL,
  `MaNguoiChoi1` int NOT NULL,
  `MaNguoiChoi2` int NOT NULL,
  `ThoiGianBatDau` datetime NOT NULL,
  `ThoiGianKetThuc` datetime DEFAULT NULL,
  `SoLuotBan_NC1` int DEFAULT '0',
  `SoLuotBan_NC2` int DEFAULT '0',
  `SoLuotTrung_NC1` int DEFAULT '0',
  `SoLuotTrung_NC2` int DEFAULT '0',
  `NguoiThang` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `lich_su_tran_dau`
--

INSERT INTO `lich_su_tran_dau` (`MaTranDau`, `MaNguoiChoi1`, `MaNguoiChoi2`, `ThoiGianBatDau`, `ThoiGianKetThuc`, `SoLuotBan_NC1`, `SoLuotBan_NC2`, `SoLuotTrung_NC1`, `SoLuotTrung_NC2`, `NguoiThang`) VALUES
(1, 1, 2, '2025-11-22 23:10:24', '2025-11-22 23:11:00', 15, 1, 14, 0, 1),
(2, 1, 2, '2025-11-22 23:11:30', '2025-11-22 23:11:47', 1, 14, 0, 14, 2),
(3, 1, 2, '2025-11-23 01:24:57', '2025-11-23 01:25:21', 1, 14, 0, 14, 2);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `quanli`
--

CREATE TABLE `quanli` (
  `id` int NOT NULL,
  `ten_dang_nhap` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mat_khau` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ngay_tao` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `quanli`
--

INSERT INTO `quanli` (`id`, `ten_dang_nhap`, `mat_khau`, `ngay_tao`) VALUES
(1, 'hung100105', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '2025-11-22 09:00:47');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `taikhoan`
--

CREATE TABLE `taikhoan` (
  `MaTaiKhoan` int NOT NULL,
  `TenDangNhap` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `MatKhau` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `SoTranThang` int DEFAULT '0',
  `SoTranThua` int DEFAULT '0',
  `NgayTao` datetime DEFAULT CURRENT_TIMESTAMP,
  `NgayCapNhat` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `taikhoan`
--

INSERT INTO `taikhoan` (`MaTaiKhoan`, `TenDangNhap`, `MatKhau`, `Email`, `SoTranThang`, `SoTranThua`, `NgayTao`, `NgayCapNhat`) VALUES
(1, 'hung123', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', NULL, 1, 2, '2025-11-22 15:58:56', '2025-11-23 01:25:21'),
(2, 'an123', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', NULL, 2, 1, '2025-11-22 15:59:23', '2025-11-23 01:25:21');

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `lich_su_tran_dau`
--
ALTER TABLE `lich_su_tran_dau`
  ADD PRIMARY KEY (`MaTranDau`),
  ADD KEY `fk_player1` (`MaNguoiChoi1`),
  ADD KEY `fk_player2` (`MaNguoiChoi2`),
  ADD KEY `fk_winner` (`NguoiThang`);

--
-- Chỉ mục cho bảng `quanli`
--
ALTER TABLE `quanli`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ten_dang_nhap` (`ten_dang_nhap`);

--
-- Chỉ mục cho bảng `taikhoan`
--
ALTER TABLE `taikhoan`
  ADD PRIMARY KEY (`MaTaiKhoan`),
  ADD UNIQUE KEY `TenDangNhap` (`TenDangNhap`),
  ADD UNIQUE KEY `Email` (`Email`);

--
-- AUTO_INCREMENT cho các bảng đã đổ
--

--
-- AUTO_INCREMENT cho bảng `lich_su_tran_dau`
--
ALTER TABLE `lich_su_tran_dau`
  MODIFY `MaTranDau` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT cho bảng `quanli`
--
ALTER TABLE `quanli`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT cho bảng `taikhoan`
--
ALTER TABLE `taikhoan`
  MODIFY `MaTaiKhoan` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Các ràng buộc cho các bảng đã đổ
--

--
-- Các ràng buộc cho bảng `lich_su_tran_dau`
--
ALTER TABLE `lich_su_tran_dau`
  ADD CONSTRAINT `fk_player1` FOREIGN KEY (`MaNguoiChoi1`) REFERENCES `taikhoan` (`MaTaiKhoan`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_player2` FOREIGN KEY (`MaNguoiChoi2`) REFERENCES `taikhoan` (`MaTaiKhoan`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_winner` FOREIGN KEY (`NguoiThang`) REFERENCES `taikhoan` (`MaTaiKhoan`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
