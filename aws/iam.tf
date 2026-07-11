# Least-privilege example: a read-only "auditor" role instead of attaching
# AdministratorAccess to anything. This is the pattern the target JDs mean by
# "least-privilege IAM" - scope permissions to what a role actually needs.

data "aws_iam_policy_document" "auditor_trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "AWS"
      identifiers = [data.aws_caller_identity.current.account_id]
    }
  }
}

data "aws_caller_identity" "current" {}

resource "aws_iam_role" "auditor" {
  name               = "${var.project_name}-auditor"
  description        = "Read-only role for compliance/audit review, scoped to this account"
  assume_role_policy = data.aws_iam_policy_document.auditor_trust.json

  tags = {
    Project = var.project_name
  }
}

# AWS-managed ReadOnlyAccess is broad; narrower custom policies are the next
# iteration once you know exactly which services this role needs to read.
resource "aws_iam_role_policy_attachment" "auditor_readonly" {
  role       = aws_iam_role.auditor.name
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}
