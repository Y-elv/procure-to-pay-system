/**
 * TypeScript types for the application.
 */

export type UserRole =
  | 'staff'
  | 'approver_level_1'
  | 'approver_level_2'
  | 'finance';

export interface User {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  first_name: string;
  last_name: string;
  date_joined: string;
}

export type RequestStatus = 'pending' | 'approved' | 'rejected';

export interface RequestItem {
  id?: number;
  item_name: string;
  quantity: number;
  price: number;
  total: number;
}

export interface Approval {
  id: number;
  approver: number;
  approver_username: string;
  approver_name: string;
  level: number;
  status: 'pending' | 'approved' | 'rejected';
  comment: string;
  created_at: string;
  updated_at: string;
}

export interface PurchaseRequest {
  id: number;
  title: string;
  description: string;
  amount: string;
  status: RequestStatus;
  created_by: number;
  created_by_username: string;
  created_by_name: string;
  proforma_file: string | null;
  purchase_order_file: string | null;
  receipt_file: string | null;
  items: RequestItem[];
  approvals: Approval[];
  can_edit: boolean;
  can_approve: boolean;
  created_at: string;
  updated_at: string;
}

export interface ReceiptValidation {
  id: number;
  is_valid: boolean;
  discrepancy_amount: string | null;
  discrepancy_details: any;
  validated_by: number;
  validated_by_username: string;
  validated_at: string;
}

