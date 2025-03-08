import React, { useState, useEffect, useMemo } from 'react'; // react ^18.2.0
import { useSelector } from 'react-redux'; // react-redux ^8.1.1
import {
  Card,
  CardContent,
  Typography,
  Checkbox,
  FormControlLabel,
  Divider,
  FormGroup,
} from '@mui/material'; // @mui/material ^5.14.0
import { Permission, Role } from '../../types/user.types';
import useStyles from './styles';

/**
 * Interface defining the props for the PermissionSelection component.
 */
interface PermissionSelectionProps {
  selectedRole: Role | null;
  selectedPermissions: string[];
  onChange: (permissions: string[]) => void;
}

/**
 * Interface defining the structure for grouped permissions.
 */
interface GroupedPermissions {
  [resourceType: string]: Permission[];
}

/**
 * Component for selecting permissions for a user role.
 * It groups permissions by resource type and allows for selecting/deselecting
 * individual permissions or entire permission groups.
 *
 * @param {PermissionSelectionProps} props - The props for the component.
 * @returns {JSX.Element} The rendered component.
 */
const PermissionSelection: React.FC<PermissionSelectionProps> = (props) => {
  const classes = useStyles();

  // Get all permissions from Redux store using useSelector
  const permissions = useSelector(selectPermissions);

  // Initialize state for selected permissions using props.selectedPermissions
  const [selected, setSelected] = useState<string[]>(props.selectedPermissions);

  // Group permissions by resourceType using useMemo
  const groupedPermissions: GroupedPermissions = useMemo(() => {
    const groups: GroupedPermissions = {};
    permissions.forEach((permission) => {
      if (!groups[permission.resourceType]) {
        groups[permission.resourceType] = [];
      }
      groups[permission.resourceType].push(permission);
    });
    return groups;
  }, [permissions]);

  // Handle permission selection/deselection with togglePermission function
  const togglePermission = (permissionId: string) => {
    setSelected((prevSelected) => {
      if (prevSelected.includes(permissionId)) {
        return prevSelected.filter((id) => id !== permissionId);
      } else {
        return [...prevSelected, permissionId];
      }
    });
  };

  // Handle group selection/deselection with toggleGroup function
  const toggleGroup = (groupPermissions: Permission[]) => {
    const permissionIds = groupPermissions.map((permission) => permission.id);
    setSelected((prevSelected) => {
      const allSelected = permissionIds.every((id) => prevSelected.includes(id));
      if (allSelected) {
        return prevSelected.filter((id) => !permissionIds.includes(id));
      } else {
        return [...prevSelected, ...permissionIds.filter((id) => !prevSelected.includes(id))];
      }
    });
  };

  // Check if all permissions in a group are selected with areAllSelected function
  const areAllSelected = (groupPermissions: Permission[]): boolean => {
    const permissionIds = groupPermissions.map((permission) => permission.id);
    return permissionIds.every((id) => selected.includes(id));
  };

  // Check if some permissions in a group are selected with areSomeSelected function
  const areSomeSelected = (groupPermissions: Permission[]): boolean => {
    const permissionIds = groupPermissions.map((permission) => permission.id);
    return permissionIds.some((id) => selected.includes(id)) && !areAllSelected(groupPermissions);
  };

  // Update parent component when selected permissions change
  useEffect(() => {
    props.onChange(selected);
  }, [selected, props.onChange]);

  // Render Card with grouped permissions
  return (
    <Card className={classes.permissionContainer}>
      <CardContent>
        {Object.entries(groupedPermissions).map(([resourceType, groupPermissions]) => (
          <div key={resourceType} className={classes.permissionGroup}>
            {/* Render each permission group with a group checkbox and individual permission checkboxes */}
            <FormControlLabel
              control={
                <Checkbox
                  checked={areAllSelected(groupPermissions)}
                  indeterminate={areSomeSelected(groupPermissions)}
                  onChange={() => toggleGroup(groupPermissions)}
                />
              }
              label={
                <Typography variant="subtitle1" className={classes.permissionGroupTitle}>
                  {resourceType}
                </Typography>
              }
            />
            <FormGroup>
              {groupPermissions.map((permission) => (
                <FormControlLabel
                  key={permission.id}
                  className={classes.permissionItem}
                  control={
                    <Checkbox
                      checked={selected.includes(permission.id)}
                      onChange={() => togglePermission(permission.id)}
                      className={classes.indentedCheckbox}
                    />
                  }
                  label={permission.name}
                />
              ))}
            </FormGroup>
            <Divider className={classes.divider} />
          </div>
        ))}
      </CardContent>
    </Card>
  );
};

export default PermissionSelection;

// Redux selector for permissions list
const selectPermissions = (state: any): Permission[] => state.user.permissions;