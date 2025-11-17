import React, { useEffect, useMemo, useState } from "react";
import { Modal, ModalBody } from "reactstrap";
import { Button, Icon, RSelect } from "@/components/Component";
import { useChangeUserRole } from "@/api/adminUserHooks";
import useAuth from "@/api/useAuth";

const BASE_ROLE_OPTIONS = [
  {
    value: "super_admin",
    label: "Super Admin",
    description: "Full system access, including management of admins and global settings.",
  },
  {
    value: "admin",
    label: "Administrator",
    description: "Full platform access including user and content management.",
  },
  {
    value: "moderator",
    label: "Moderator",
    description: "Can moderate content and manage community interactions.",
  },
  {
    value: "user",
    label: "User",
    description: "Standard access for reading and creating content.",
  },
];

const RoleModal = ({ isOpen, onClose, userUuid, currentRole, onRoleChange }) => {
  const { mutate: changeRole, loading, error } = useChangeUserRole();
  const { auth } = useAuth();

  const [selectedRole, setSelectedRole] = useState(currentRole || "user");
  const [reason, setReason] = useState("");
  const [confirmText, setConfirmText] = useState("");

  useEffect(() => {
    if (currentRole) {
      setSelectedRole(currentRole);
    }
    setReason("");
    setConfirmText("");
  }, [currentRole, isOpen]);

  const currentUserRole = (auth?.user?.role || "").toLowerCase();

  const roleOptions = useMemo(() => {
    // Only super-admins are allowed to change roles; others should not see the selector
    if (currentUserRole === "super_admin") {
      return BASE_ROLE_OPTIONS;
    }

    // Fallback: show only the current role as a non-editable option
    return BASE_ROLE_OPTIONS.filter((option) => option.value === currentRole);
  }, [currentUserRole, currentRole]);

  const selectedOption = useMemo(
    () => roleOptions.find((option) => option.value === selectedRole) || null,
    [selectedRole, roleOptions]
  );

  const requiresStrongConfirmation =
    selectedRole === "admin" || selectedRole === "super_admin";

  const isConfirmValid = !requiresStrongConfirmation || confirmText.trim().toUpperCase() === "CONFIRM";

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!userUuid || !selectedRole || !isConfirmValid) return;
    // Extra guard: only super-admins should be able to submit role changes
    if (currentUserRole !== "super_admin") return;
    try {
      const response = await changeRole(userUuid, selectedRole, reason || undefined);
      if (onRoleChange && response?.data) {
        onRoleChange(response.data);
      }
      onClose();
    } catch (err) {
      console.error("Failed to update role", err);
    }
  };

  return (
    <Modal isOpen={isOpen} toggle={onClose} className="modal-dialog-centered" size="lg">
      <ModalBody>
        <a
          href="#close"
          onClick={(ev) => {
            ev.preventDefault();
            onClose();
          }}
          className="close"
        >
          <Icon name="cross-sm"></Icon>
        </a>
        <div className="p-2">
          <h5 className="title mb-3">Change User Role</h5>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Select Role</label>
              <RSelect
                options={roleOptions}
                value={selectedOption}
                placeholder="Choose a role"
                onChange={(option) => setSelectedRole(option?.value || "user")}
              />
              {selectedOption && (
                <div className="text-soft mt-2 small">{selectedOption.description}</div>
              )}
            </div>
            <div className="form-group">
              <label className="form-label">Reason (optional)</label>
              <textarea
                className="form-control"
                rows="3"
                placeholder="Explain why this role is being changed (for audit history)."
                value={reason}
                onChange={(e) => setReason(e.target.value)}
              />
            </div>
            {requiresStrongConfirmation && (
              <div className="form-group">
                <div className="alert alert-warning py-2 mb-2" role="alert">
                  This will grant high-level administrative access. Type <strong>CONFIRM</strong>{" "}
                  below to continue.
                </div>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Type CONFIRM to proceed"
                  value={confirmText}
                  onChange={(e) => setConfirmText(e.target.value)}
                />
              </div>
            )}
            {error && (
              <div className="alert alert-danger py-2" role="alert">
                {error}
              </div>
            )}
            <div className="d-flex justify-content-end gap-2 mt-3">
              <Button color="light" type="button" onClick={onClose}>
                Cancel
              </Button>
              <Button color="primary" type="submit" disabled={loading || !selectedRole || !isConfirmValid}>
                <Icon name="save"></Icon>
                <span>Update Role</span>
              </Button>
            </div>
          </form>
        </div>
      </ModalBody>
    </Modal>
  );
};

export default RoleModal;

