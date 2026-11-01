'use strict';

class Notice {
  constructor(member) {
    this.member = member;
  }

  render() {
    throw new Error('not implemented');
  }
}

class OverdueNotice extends Notice {
  constructor(member, loans) {
    super(member);
    this.loans = loans;
  }

  render() {
    const titles = this.loans.map((loan) => `${loan.title} (due ${formatDueDate(loan.dueDate)})`);
    return `Dear ${this.member.name}, please return: ${titles.join('; ')}`;
  }
}

function formatDueDate(date) {
  if (Number.isNaN(date.getTime())) return 'unknown date';
  return date.toISOString().slice(0, 10);
}

module.exports = { Notice, OverdueNotice };
